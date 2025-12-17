import React from 'react';
import './ChatInterface.css';

export default function AttachmentPreview({ attachments, onRemove }) {
  if (!attachments || attachments.length === 0) return null;

  return (
    <div className="attachment-preview-container">
      {attachments.map((att, index) => (
        <div key={index} className="attachment-preview-item">
          <div className="attachment-thumbnail">
            {att.type === 'image' ? (
              <img src={att.data} alt={att.filename} />
            ) : (
              <div className="file-icon">
                📄
                <span className="file-ext">{att.filename.split('.').pop()}</span>
              </div>
            )}
          </div>
          <div className="attachment-info">
            <span className="attachment-name" title={att.filename}>
              {att.filename}
            </span>
            <button 
              className="remove-attachment-btn"
              onClick={() => onRemove(index)}
              type="button"
            >
              ×
            </button>
          </div>
        </div>
      ))}
    </div>
  );
}
