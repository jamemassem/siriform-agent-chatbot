"""SiriAgent - AI-powered form filling assistant using LangGraph.

This module implements the core agent logic using the ReAct pattern:
1. Reason about user input
2. Act using available tools
3. Observe results and iterate

The agent orchestrates 6 specialized tools to progressively fill forms
through conversational interactions.
"""
from typing import Any, Dict, List, Optional, Sequence, TypedDict
import json

from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain_core.language_models import BaseChatModel
from langchain_core.tracers import LangChainTracer
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolExecutor, ToolInvocation

from app.agent.tools.history import lookup_user_history
from app.agent.tools.analyzer import analyze_user_request
from app.agent.tools.lookup import lookup_information
from app.agent.tools.form_writer import update_form_data
from app.agent.tools.validator import validate_field
from app.agent.tools.question_asker import ask_clarifying_question


class AgentState(TypedDict):
    """State maintained throughout the agent's execution."""
    messages: Sequence[BaseMessage]
    form_data: Dict[str, Any]
    form_schema: Dict[str, Any]
    session_id: str
    highlighted_fields: List[str]
    confidence: float
    next_action: str  # "continue", "need_clarification", "done"


class SiriAgent:
    """Conversational agent for progressive form filling.
    
    The agent uses a ReAct cycle to:
    1. Analyze user's natural language input
    2. Look up relevant information from history or schema
    3. Validate and update form data
    4. Ask clarifying questions when needed
    5. Provide confidence scores for extracted information
    
    Attributes:
        llm: Language model for reasoning and tool selection
        supabase_client: Client for accessing user history
        form_schema: JSON Schema of the form being filled
    """
    
    def __init__(
        self,
        llm: BaseChatModel,
        supabase_client: Any,
        form_schema: Dict[str, Any]
    ):
        """Initialize the SiriAgent.
        
        Args:
            llm: LangChain chat model instance
            supabase_client: Supabase client for database access
            form_schema: JSON Schema definition of the form
        """
        self.llm = llm
        self.supabase_client = supabase_client
        self.form_schema = form_schema
        self.graph = self._create_graph()
    
    def _create_graph(self) -> StateGraph:
        """Create the LangGraph state machine for the agent.
        
        Returns:
            StateGraph configured with agent workflow
        """
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("analyze", self._analyze_node)
        workflow.add_node("lookup_history", self._lookup_history_node)
        workflow.add_node("update_form", self._update_form_node)
        workflow.add_node("validate", self._validate_node)
        workflow.add_node("ask_question", self._ask_question_node)
        
        # Define edges (workflow)
        workflow.set_entry_point("analyze")
        workflow.add_edge("analyze", "lookup_history")
        workflow.add_edge("lookup_history", "update_form")
        workflow.add_edge("update_form", "validate")
        
        # Conditional edge: validate -> ask_question or END
        workflow.add_conditional_edges(
            "validate",
            self._should_ask_question,
            {
                "ask": "ask_question",
                "done": END
            }
        )
        workflow.add_edge("ask_question", END)
        
        return workflow.compile()
    
    async def _analyze_node(self, state: AgentState) -> AgentState:
        """Analyze user's message and extract structured information.
        
        Args:
            state: Current agent state
            
        Returns:
            Updated state with extracted data and confidence
        """
        # Get the latest user message
        user_message = next(
            (msg.content for msg in reversed(state["messages"]) 
             if isinstance(msg, HumanMessage)),
            ""
        )
        
        # Use the analyzer tool
        analysis = await analyze_user_request(
            user_message=user_message,
            form_schema=self.form_schema,
            llm_client=self.llm
        )
        
        # Update state with analysis results
        state["confidence"] = analysis["confidence"]
        
        # Store extracted data temporarily (will be merged in update_form node)
        state["_extracted_data"] = analysis["extracted_data"]
        state["_ambiguities"] = analysis["ambiguities"]
        
        return state
    
    async def _lookup_history_node(self, state: AgentState) -> AgentState:
        """Look up user's previous submissions for context.
        
        Args:
            state: Current agent state
            
        Returns:
            Updated state with historical context
        """
        history = await lookup_user_history(
            supabase_client=self.supabase_client,
            session_id=state["session_id"],
            limit=3
        )
        
        # If user has history, add it to context
        if history:
            context_msg = SystemMessage(
                content=f"User's previous submissions: {json.dumps(history, ensure_ascii=False)}"
            )
            state["messages"].append(context_msg)
        
        return state
    
    async def _update_form_node(self, state: AgentState) -> AgentState:
        """Update form data with extracted information.
        
        Args:
            state: Current agent state
            
        Returns:
            Updated state with merged form data
        """
        extracted_data = state.get("_extracted_data", {})
        current_form_data = state["form_data"]
        highlighted_fields = []
        
        # Update each extracted field
        for field_name, value in extracted_data.items():
            try:
                updated_data = await update_form_data(
                    current_form_data=current_form_data,
                    field_path=field_name,
                    new_value=value,
                    form_schema=self.form_schema,
                    validate=False  # We'll validate in the next node
                )
                current_form_data = updated_data
                highlighted_fields.append(field_name)
            except Exception as e:
                # Log error but continue processing other fields
                print(f"Error updating field {field_name}: {e}")
        
        state["form_data"] = current_form_data
        state["highlighted_fields"] = highlighted_fields
        
        return state
    
    async def _validate_node(self, state: AgentState) -> AgentState:
        """Validate all updated fields against the schema.
        
        Args:
            state: Current agent state
            
        Returns:
            Updated state with validation results
        """
        form_data = state["form_data"]
        validation_errors = []
        
        # Validate each field that was just updated
        for field_name in state["highlighted_fields"]:
            if field_name in form_data:
                is_valid, error_msg = await validate_field(
                    field_name=field_name,
                    value=form_data[field_name],
                    form_schema=self.form_schema
                )
                
                if not is_valid:
                    validation_errors.append({
                        "field": field_name,
                        "error": error_msg
                    })
        
        # Store validation results
        state["_validation_errors"] = validation_errors
        
        # Adjust confidence based on validation
        if validation_errors:
            state["confidence"] *= 0.7  # Reduce confidence if validation fails
        
        return state
    
    def _should_ask_question(self, state: AgentState) -> str:
        """Determine if we should ask a clarifying question.
        
        Args:
            state: Current agent state
            
        Returns:
            "ask" if clarification needed, "done" otherwise
        """
        # Ask question if:
        # 1. Confidence is low (< 0.7)
        # 2. There are ambiguous fields
        # 3. There are validation errors
        
        has_ambiguities = len(state.get("_ambiguities", [])) > 0
        has_validation_errors = len(state.get("_validation_errors", [])) > 0
        low_confidence = state["confidence"] < 0.7
        
        if has_ambiguities or has_validation_errors or low_confidence:
            return "ask"
        return "done"
    
    async def _ask_question_node(self, state: AgentState) -> AgentState:
        """Generate a clarifying question for the user.
        
        Args:
            state: Current agent state
            
        Returns:
            Updated state with generated question
        """
        # Determine what to ask about
        ambiguous_fields = state.get("_ambiguities", [])
        validation_errors = state.get("_validation_errors", [])
        
        # Prioritize validation errors over ambiguities
        if validation_errors:
            field_name = validation_errors[0]["field"]
            error_msg = validation_errors[0]["error"]
            question = f"ขออภัยครับ {error_msg} กรุณาระบุใหม่อีกครั้งครับ"
        elif ambiguous_fields:
            # Use the question asker tool
            context = {
                "extracted_data": state.get("_extracted_data", {}),
                "confidence": state["confidence"],
                "user_message": next(
                    (msg.content for msg in reversed(state["messages"]) 
                     if isinstance(msg, HumanMessage)),
                    ""
                )
            }
            
            question = await ask_clarifying_question(
                ambiguous_fields=ambiguous_fields,
                form_schema=self.form_schema,
                context=context,
                language="th"
            )
        else:
            # Generic low confidence question
            question = "ขอบคุณครับ ช่วยอธิบายเพิ่มเติมอีกนิดได้ไหมครับ?"
        
        # Add AI message to conversation
        state["messages"].append(AIMessage(content=question))
        state["next_action"] = "need_clarification"
        
        return state
    
    async def process_message(
        self,
        user_message: str,
        session_id: str,
        current_form_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Process a user message and return the agent's response.
        
        Args:
            user_message: User's natural language input
            session_id: Session identifier for conversation tracking
            current_form_data: Current state of the form (optional)
            
        Returns:
            Dictionary containing:
            - response: Agent's response text
            - form_data: Updated form data
            - highlighted_fields: List of fields that were updated
            - confidence: Confidence score (0.0 to 1.0)
        """
        # Initialize state
        initial_state: AgentState = {
            "messages": [HumanMessage(content=user_message)],
            "form_data": current_form_data or {},
            "form_schema": self.form_schema,
            "session_id": session_id,
            "highlighted_fields": [],
            "confidence": 0.0,
            "next_action": "continue"
        }
        
        # Run the graph
        final_state = await self.graph.ainvoke(initial_state)
        
        # Extract response from the last AI message
        response_text = next(
            (msg.content for msg in reversed(final_state["messages"]) 
             if isinstance(msg, AIMessage)),
            "ขอบคุณครับ มีอะไรให้ช่วยเพิ่มเติมไหมครับ?"
        )
        
        return {
            "response": response_text,
            "form_data": final_state["form_data"],
            "highlighted_fields": final_state["highlighted_fields"],
            "confidence": final_state["confidence"]
        }
