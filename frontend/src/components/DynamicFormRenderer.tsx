/**
 * DynamicFormRenderer component
 * Renders a form dynamically from JSON Schema with Thai language support
 */
import React from 'react';
import type { JSONSchema, FormData } from '../types';
import { getFieldLabel, isFieldRequired } from '../utils/formUtils';
import './DynamicFormRenderer.css';

interface DynamicFormRendererProps {
  schema: JSONSchema;
  formData: FormData;
  highlightedFields?: string[];
  readOnly?: boolean;
  onFieldChange?: (fieldName: string, value: any) => void;
}

export const DynamicFormRenderer: React.FC<DynamicFormRendererProps> = ({
  schema,
  formData,
  highlightedFields = [],
  readOnly = false,
  onFieldChange,
}) => {
  const properties = schema.properties || {};

  const handleChange = (fieldName: string, value: any) => {
    if (!readOnly && onFieldChange) {
      onFieldChange(fieldName, value);
    }
  };

  const renderField = (fieldName: string) => {
    const property = properties[fieldName];
    if (!property) return null;

    const label = getFieldLabel(fieldName, schema);
    const isRequired = isFieldRequired(fieldName, schema);
    const isHighlighted = highlightedFields.includes(fieldName);
    const value = formData[fieldName];

    const fieldClass = `form-field ${isHighlighted ? 'highlighted' : ''}`;

    // Render different input types based on schema
    switch (property.type) {
      case 'string':
        if (property.enum) {
          // Enum select dropdown
          return (
            <div key={fieldName} className={fieldClass}>
              <label htmlFor={fieldName} className="form-label">
                {label}
                {isRequired && <span className="required-star">*</span>}
              </label>
              <select
                id={fieldName}
                value={value || ''}
                onChange={(e) => handleChange(fieldName, e.target.value)}
                disabled={readOnly}
                className="form-select"
                required={isRequired}
              >
                <option value="">-- เลือก --</option>
                {property.enum.map((option) => (
                  <option key={option} value={option}>
                    {option}
                  </option>
                ))}
              </select>
            </div>
          );
        } else if (property.format === 'date') {
          // Date input
          return (
            <div key={fieldName} className={fieldClass}>
              <label htmlFor={fieldName} className="form-label">
                {label}
                {isRequired && <span className="required-star">*</span>}
              </label>
              <input
                id={fieldName}
                type="date"
                value={value || ''}
                onChange={(e) => handleChange(fieldName, e.target.value)}
                disabled={readOnly}
                className="form-input"
                required={isRequired}
              />
            </div>
          );
        } else if (property.format === 'time') {
          // Time input
          return (
            <div key={fieldName} className={fieldClass}>
              <label htmlFor={fieldName} className="form-label">
                {label}
                {isRequired && <span className="required-star">*</span>}
              </label>
              <input
                id={fieldName}
                type="time"
                value={value || ''}
                onChange={(e) => handleChange(fieldName, e.target.value)}
                disabled={readOnly}
                className="form-input"
                required={isRequired}
              />
            </div>
          );
        } else if (property.maxLength && property.maxLength > 100) {
          // Textarea for long text
          return (
            <div key={fieldName} className={fieldClass}>
              <label htmlFor={fieldName} className="form-label">
                {label}
                {isRequired && <span className="required-star">*</span>}
              </label>
              <textarea
                id={fieldName}
                value={value || ''}
                onChange={(e) => handleChange(fieldName, e.target.value)}
                disabled={readOnly}
                className="form-textarea"
                required={isRequired}
                rows={4}
                maxLength={property.maxLength}
              />
            </div>
          );
        } else {
          // Regular text input
          return (
            <div key={fieldName} className={fieldClass}>
              <label htmlFor={fieldName} className="form-label">
                {label}
                {isRequired && <span className="required-star">*</span>}
              </label>
              <input
                id={fieldName}
                type="text"
                value={value || ''}
                onChange={(e) => handleChange(fieldName, e.target.value)}
                disabled={readOnly}
                className="form-input"
                required={isRequired}
                pattern={property.pattern}
                minLength={property.minLength}
                maxLength={property.maxLength}
                placeholder={property.description}
              />
            </div>
          );
        }

      case 'integer':
      case 'number':
        return (
          <div key={fieldName} className={fieldClass}>
            <label htmlFor={fieldName} className="form-label">
              {label}
              {isRequired && <span className="required-star">*</span>}
            </label>
            <input
              id={fieldName}
              type="number"
              value={value || ''}
              onChange={(e) => handleChange(fieldName, parseFloat(e.target.value))}
              disabled={readOnly}
              className="form-input"
              required={isRequired}
              min={property.minimum}
              max={property.maximum}
            />
          </div>
        );

      case 'array':
        // For equipment array - show summary
        if (fieldName === 'equipments' && Array.isArray(value)) {
          return (
            <div key={fieldName} className={fieldClass}>
              <label className="form-label">
                {label}
                {isRequired && <span className="required-star">*</span>}
              </label>
              <div className="equipment-list">
                {value.length === 0 ? (
                  <p className="empty-text">ยังไม่ได้ระบุอุปกรณ์</p>
                ) : (
                  value.map((item: any, index: number) => (
                    <div key={index} className="equipment-item">
                      <span className="equipment-type">{item.type}</span>
                      <span className="equipment-qty">จำนวน: {item.quantity}</span>
                      {item.detail && (
                        <span className="equipment-detail">{item.detail}</span>
                      )}
                    </div>
                  ))
                )}
              </div>
            </div>
          );
        }
        return null;

      case 'boolean':
        return (
          <div key={fieldName} className={fieldClass}>
            <label className="form-checkbox-label">
              <input
                type="checkbox"
                checked={value || false}
                onChange={(e) => handleChange(fieldName, e.target.checked)}
                disabled={readOnly}
                className="form-checkbox"
              />
              <span>{label}</span>
              {isRequired && <span className="required-star">*</span>}
            </label>
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <div className="dynamic-form">
      <div className="form-header">
        <h2 className="form-title">{schema.title || 'แบบฟอร์ม'}</h2>
        {schema.description && (
          <p className="form-description">{schema.description}</p>
        )}
      </div>
      <div className="form-fields">
        {Object.keys(properties).map((fieldName) => renderField(fieldName))}
      </div>
    </div>
  );
};

export default DynamicFormRenderer;
