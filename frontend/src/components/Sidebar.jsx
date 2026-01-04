import React from 'react';

function Sidebar({
  collapsed,
  mobileOpen,
  onToggleCollapse,
  sessions,
  selectedSession,
  onSelectSession,
  onDeleteSession,
  onDeleteAll,
  onNewChat,
}) {
  return (
    <div className={`sidebar ${collapsed ? 'collapsed' : 'expanded'} ${mobileOpen ? 'mobile-open' : ''}`}>
      <div className="sidebar-header">
        {!collapsed && <h2 className="sidebar-title">Guru Multibot</h2>}
        
        <button
          onClick={onToggleCollapse}
          className="action-btn sidebar-toggle-btn"
          style={{ opacity: mobileOpen ? 0 : 1 }}
        >
          {collapsed ? "→" : "←"}
        </button>
      </div>

      <div style={{ padding: "0 16px 20px" }}>
        <button
          onClick={onNewChat}
          className="send-btn"
          style={{
            width: "100%",
            height: "48px",
            border: "none",
            borderRadius: "var(--radius-md)",
            fontSize: "0.95rem",
            fontWeight: "600",
            display: "flex",
            alignItems: "center",
            justifyContent: collapsed ? "center" : "flex-start",
            gap: "12px",
            padding: collapsed ? "0" : "0 16px",
            transition: "var(--transition)",
            cursor: "pointer"
          }}
        >
          <span>✨</span>
          {!collapsed && "New Conversation"}
        </button>
      </div>

      <div className="sidebar-content" style={{ flex: 1, overflowY: "auto", padding: "0 16px" }}>
        {!collapsed && (
          <div style={{ 
            fontSize: "0.75rem", 
            color: "var(--text-dim)", 
            fontWeight: "700", 
            textTransform: "uppercase", 
            letterSpacing: "1px",
            margin: "20px 0 12px 4px"
          }}>
            Recent History
          </div>
        )}

        {sessions.map((session) => (
          <div
            key={session.session_id}
            onClick={() => onSelectSession(session)}
            style={{
              padding: "10px 12px",
              marginBottom: "4px",
              borderRadius: "var(--radius-md)",
              cursor: "pointer",
              backgroundColor: selectedSession?.session_id === session.session_id ? "var(--bg-surface-light)" : "transparent",
              color: selectedSession?.session_id === session.session_id ? "var(--text-main)" : "var(--text-muted)",
              display: "flex",
              alignItems: "center",
              gap: "12px",
              transition: "var(--transition)",
              whiteSpace: "nowrap",
              overflow: "hidden"
            }}
            className="sidebar-item"
          >
            <span style={{ fontSize: "1.1rem" }}>💬</span>
            {!collapsed && (
              <span style={{ 
                flex: 1, 
                overflow: "hidden", 
                textOverflow: "ellipsis",
                fontSize: "0.9rem"
              }}>
                {session.session_title}
              </span>
            )}
          </div>
        ))}
      </div>

      {sessions.length > 0 && !collapsed && (
        <div style={{ padding: "16px", borderTop: "1px solid var(--glass-border)" }}>
          <button
            onClick={onDeleteAll}
            style={{
              width: "100%",
              padding: "8px",
              background: "transparent",
              border: "1px solid var(--glass-border)",
              borderRadius: "var(--radius-sm)",
              color: "#f87171",
              fontSize: "0.8rem",
              cursor: "pointer",
              transition: "var(--transition)"
            }}
            onMouseOver={(e) => e.target.style.background = "rgba(244, 63, 94, 0.1)"}
            onMouseOut={(e) => e.target.style.background = "transparent"}
          >
            Clear All History
          </button>
        </div>
      )}
    </div>
  );
}

export default Sidebar;
