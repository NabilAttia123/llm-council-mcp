import { useState, useRef, useEffect } from 'react';
import './Sidebar.css';

export default function Sidebar({
  conversations,
  currentConversationId,
  onSelectConversation,
  onNewConversation,
  onDeleteConversation,
  onRenameConversation,
}) {
  const [menuOpenId, setMenuOpenId] = useState(null);
  const [renamingId, setRenamingId] = useState(null);
  const [renameValue, setRenameValue] = useState('');
  const [deleteConfirmId, setDeleteConfirmId] = useState(null);
  const menuRef = useRef(null);
  const renameInputRef = useRef(null);

  // Close menu when clicking outside
  useEffect(() => {
    const handleClickOutside = (e) => {
      if (menuRef.current && !menuRef.current.contains(e.target)) {
        setMenuOpenId(null);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Focus rename input when it appears
  useEffect(() => {
    if (renamingId && renameInputRef.current) {
      renameInputRef.current.focus();
      renameInputRef.current.select();
    }
  }, [renamingId]);

  const handleMenuClick = (e, convId) => {
    e.stopPropagation();
    setMenuOpenId(menuOpenId === convId ? null : convId);
  };

  const handleRenameStart = (conv) => {
    setRenamingId(conv.id);
    setRenameValue(conv.title || 'New Conversation');
    setMenuOpenId(null);
  };

  const handleRenameSubmit = (convId) => {
    if (renameValue.trim()) {
      onRenameConversation(convId, renameValue.trim());
    }
    setRenamingId(null);
    setRenameValue('');
  };

  const handleRenameKeyDown = (e, convId) => {
    if (e.key === 'Enter') {
      handleRenameSubmit(convId);
    } else if (e.key === 'Escape') {
      setRenamingId(null);
      setRenameValue('');
    }
  };

  const handleDeleteClick = (convId) => {
    setDeleteConfirmId(convId);
    setMenuOpenId(null);
  };

  const handleDeleteConfirm = (convId) => {
    onDeleteConversation(convId);
    setDeleteConfirmId(null);
  };

  const handleDeleteCancel = () => {
    setDeleteConfirmId(null);
  };

  return (
    <div className="sidebar">
      <div className="sidebar-header">
        <button className="new-conversation-btn" onClick={onNewConversation}>
          + New Conversation
        </button>
      </div>

      <div className="conversation-list">
        {conversations.length === 0 ? (
          <div className="no-conversations">No conversations yet</div>
        ) : (
          conversations.map((conv) => (
            <div
              key={conv.id}
              className={`conversation-item ${conv.id === currentConversationId ? 'active' : ''}`}
              onClick={() => onSelectConversation(conv.id)}
            >
              {renamingId === conv.id ? (
                <input
                  ref={renameInputRef}
                  type="text"
                  className="rename-input"
                  value={renameValue}
                  onChange={(e) => setRenameValue(e.target.value)}
                  onKeyDown={(e) => handleRenameKeyDown(e, conv.id)}
                  onBlur={() => handleRenameSubmit(conv.id)}
                  onClick={(e) => e.stopPropagation()}
                />
              ) : deleteConfirmId === conv.id ? (
                <div className="delete-confirm" onClick={(e) => e.stopPropagation()}>
                  <span className="delete-confirm-text">Delete?</span>
                  <button
                    className="delete-confirm-btn yes"
                    onClick={() => handleDeleteConfirm(conv.id)}
                  >
                    Yes
                  </button>
                  <button
                    className="delete-confirm-btn no"
                    onClick={handleDeleteCancel}
                  >
                    No
                  </button>
                </div>
              ) : (
                <>
                  <div className="conversation-content">
                    <div className="conversation-title">
                      {conv.title || 'New Conversation'}
                    </div>
                    <div className="conversation-meta">
                      {conv.message_count} messages
                    </div>
                  </div>
                  <button
                    className="action-menu-btn"
                    onClick={(e) => handleMenuClick(e, conv.id)}
                    aria-label="Conversation actions"
                  >
                    ⋮
                  </button>
                  {menuOpenId === conv.id && (
                    <div className="action-menu" ref={menuRef}>
                      <button
                        className="action-menu-item"
                        onClick={(e) => {
                          e.stopPropagation();
                          handleRenameStart(conv);
                        }}
                      >
                        ✏️ Rename
                      </button>
                      <button
                        className="action-menu-item delete"
                        onClick={(e) => {
                          e.stopPropagation();
                          handleDeleteClick(conv.id);
                        }}
                      >
                        🗑️ Delete
                      </button>
                    </div>
                  )}
                </>
              )}
            </div>
          ))
        )}
      </div>
    </div>
  );
}
