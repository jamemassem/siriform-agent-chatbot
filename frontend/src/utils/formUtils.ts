/**
 * Utility functions for form operations.
 */
import type { JSONSchema, FormData, FormProgress } from '../types';

/**
 * Check if a field value is filled (not empty)
 */
export function isFieldFilled(value: any): boolean {
  if (value === null || value === undefined) return false;
  if (typeof value === 'string') return value.trim().length > 0;
  if (typeof value === 'number') return true;
  if (typeof value === 'boolean') return true;
  if (Array.isArray(value)) return value.length > 0;
  if (typeof value === 'object') return Object.keys(value).length > 0;
  return false;
}

/**
 * Calculate form completion progress
 */
export function calculateFormProgress(
  formData: FormData,
  schema: JSONSchema
): FormProgress {
  const properties = schema.properties || {};
  const required = schema.required || [];
  
  const totalFields = Object.keys(properties).length;
  const requiredFields = required.length;
  
  let filledFields = 0;
  let filledRequiredFields = 0;
  
  for (const [fieldName, value] of Object.entries(formData)) {
    if (isFieldFilled(value)) {
      filledFields++;
      if (required.includes(fieldName)) {
        filledRequiredFields++;
      }
    }
  }
  
  // Calculate percentage based on required fields if they exist
  // Otherwise use all fields
  const percentage = requiredFields > 0
    ? Math.round((filledRequiredFields / requiredFields) * 100)
    : Math.round((filledFields / totalFields) * 100);
  
  return {
    totalFields,
    filledFields,
    requiredFields,
    filledRequiredFields,
    percentage: Math.min(percentage, 100), // Cap at 100%
  };
}

/**
 * Get field label from schema (supports Thai labels)
 */
export function getFieldLabel(
  fieldName: string,
  schema: JSONSchema
): string {
  const property = schema.properties?.[fieldName];
  return property?.title || fieldName;
}

/**
 * Get field type from schema
 */
export function getFieldType(
  fieldName: string,
  schema: JSONSchema
): string {
  const property = schema.properties?.[fieldName];
  return property?.type || 'string';
}

/**
 * Check if field is required
 */
export function isFieldRequired(
  fieldName: string,
  schema: JSONSchema
): boolean {
  return schema.required?.includes(fieldName) || false;
}

/**
 * Format date for display (Thai Buddhist calendar)
 */
export function formatDate(dateString: string): string {
  if (!dateString) return '';
  
  const date = new Date(dateString);
  
  // Convert to Thai Buddhist year (CE + 543)
  const thaiYear = date.getFullYear() + 543;
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = String(date.getDate()).padStart(2, '0');
  
  return `${day}/${month}/${thaiYear}`;
}

/**
 * Format time for display (24-hour format)
 */
export function formatTime(timeString: string): string {
  if (!timeString) return '';
  return timeString; // Already in HH:MM format
}
