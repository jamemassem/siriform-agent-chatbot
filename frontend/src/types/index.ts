/**
 * Type definitions for the SiriForm Agent Chatbot application.
 */

/**
 * JSON Schema type definition
 */
export interface JSONSchema {
  $schema?: string;
  title?: string;
  description?: string;
  type: string;
  properties?: Record<string, JSONSchemaProperty>;
  required?: string[];
  version?: string;
}

export interface JSONSchemaProperty {
  type: string;
  title?: string;
  description?: string;
  enum?: string[];
  pattern?: string;
  format?: string;
  minLength?: number;
  maxLength?: number;
  minimum?: number;
  maximum?: number;
  minItems?: number;
  maxItems?: number;
  items?: JSONSchemaProperty;
  properties?: Record<string, JSONSchemaProperty>;
  required?: string[];
  oneOf?: Array<{ const: string; title: string }>;
}

/**
 * Chat message types
 */
export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  highlighted_fields?: string[];
  confidence?: number;
}

/**
 * Form data type (dynamic based on schema)
 */
export type FormData = Record<string, any>;

/**
 * API Request/Response types
 */
export interface ChatRequest {
  message: string;
  session_id: string;
  form_data: FormData;
}

export interface ChatResponse {
  response: string;
  form_data: FormData;
  highlighted_fields: string[];
  confidence: number;
}

export interface FormSchemaResponse {
  name: string;
  version: string;
  schema: JSONSchema;
}

export interface HealthResponse {
  status: string;
  version: string;
}

/**
 * Equipment type (specific to equipment_form schema)
 */
export interface Equipment {
  type: string;
  quantity: number;
  detail: string;
}

/**
 * Form completion calculation
 */
export interface FormProgress {
  totalFields: number;
  filledFields: number;
  requiredFields: number;
  filledRequiredFields: number;
  percentage: number;
}

/**
 * API Error response
 */
export interface APIError {
  detail: string;
  status_code: number;
}
