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
    <div
      className={`sidebar ${collapsed ? 'collapsed' : 'expanded'} ${mobileOpen ? 'mobile-open' : ''}`}
    >
      <div className="sidebar-header">
        {!collapsed && (
          <h2 className="sidebar-title">
            AI Guru Multibot
          </h2>
        )}
        
        {/* Mobile Close Button */}
        {mobileOpen && (
          <button
            onClick={() => onSelectSession(null)} // This is just a way to trigger parent state if needed, but App.js handles overlay
            className="mobile-close-btn"
            style={{
              background: "rgba(255, 255, 255, 0.1)",
              border: "none",
              borderRadius: "8px",
              padding: "8px 12px",
              color: "white",
              cursor: "pointer",
              fontSize: "18px",
              display: "none" // Managed by CSS media query if we had a class, but I'll add a class
            }}
          >
            ✕
          </button>
        )}

        <button
          onClick={onToggleCollapse}
          className="button-hover sidebar-toggle-btn"
          style={{
            background: "rgba(255, 255, 255, 0.1)",
            border: "none",
            borderRadius: "8px",
            padding: "8px",
            color: "white",
            cursor: "pointer",
            fontSize: "16px",
            transition: "all 0.2s ease",
          }}
        >
          {collapsed ? "→" : "←"}
        </button>
      </div>

      {/* New Chat Button */}
      <div style={{ padding: "16px" }}>
        <button
          onClick={onNewChat}
          className="button-hover"
          style={{
            width: "100%",
            padding: collapsed ? "16px 8px" : "14px 16px",
            background: "linear-gradient(135deg, #697565, #3C3D37)",
            color: "#ECDFCC",
            border: "none",
            borderRadius: "12px",
            fontSize: "14px",
            cursor: "pointer",
            display: "flex",
            alignItems: "center",
            justifyContent: collapsed ? "center" : "flex-start",
            gap: collapsed ? "0" : "10px",
            transition: "all 0.3s cubic-bezier(0.4, 0, 0.2, 1)",
            fontWeight: "600",
            boxShadow: "0 4px 15px rgba(105, 117, 101, 0.3)",
            position: "relative",
            overflow: "hidden",
          }}
          onMouseOver={(e) => {
            e.target.style.transform = "translateY(-2px)";
            e.target.style.boxShadow =
              "0 8px 25px rgba(105, 117, 101, 0.4)";
          }}
          onMouseOut={(e) => {
            e.target.style.transform = "translateY(0)";
            e.target.style.boxShadow =
              "0 4px 15px rgba(105, 117, 101, 0.3)";
          }}
        >
          <span
            style={{
              fontSize: "18px",
              filter: "drop-shadow(0 0 2px rgba(255,255,255,0.5))",
            }}
          >
            ✨
          </span>
          {!collapsed && "New Chat"}
        </button>
      </div>

      {/* Chat History */}
      <div
        style={{
          flex: 1,
          overflowY: "auto",
          padding: "0 16px",
          scrollbarWidth: "thin",
          scrollbarColor: "#374151 transparent",
        }}
      >
        {!collapsed && (
          <div
            style={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
              marginBottom: "12px",
            }}
          >
            <div
              style={{
                fontSize: "12px",
                color: "#9ca3af",
                fontWeight: "600",
                textTransform: "uppercase",
                letterSpacing: "0.8px",
                opacity: 0.7,
              }}
            >
              Recent Chats
            </div>
            {sessions.length > 0 && (
              <button
                onClick={onDeleteAll}
                style={{
                  background: "transparent",
                  border: "1px solid #4b5563",
                  borderRadius: "4px",
                  color: "#9ca3af",
                  fontSize: "10px",
                  padding: "3px 6px",
                  cursor: "pointer",
                  transition: "all 0.2s ease",
                }}
                onMouseEnter={(e) => {
                  e.target.style.backgroundColor = "#dc2626";
                  e.target.style.borderColor = "#dc2626";
                  e.target.style.color = "white";
                }}
                onMouseLeave={(e) => {
                  e.target.style.backgroundColor = "transparent";
                  e.target.style.borderColor = "#4b5563";
                  e.target.style.color = "#9ca3af";
                }}
                title="Delete all chat history"
              >
                Clear All
              </button>
            )}
          </div>
        )}

        {sessions.length === 0 ? (
          <div
            style={{
              color: "#6b7280",
              fontSize: "13px",
              fontStyle: "italic",
              textAlign: collapsed ? "center" : "left",
              padding: "8px 0",
            }}
          >
            {collapsed ? "📝" : "No conversations yet"}
          </div>
        ) : (
          sessions.map((session, index) => (
            <div
              key={session.session_id}
              style={{
                display: "flex",
                alignItems: "center",
                padding: "8px 12px",
                marginBottom: "4px",
                borderRadius: "6px",
                backgroundColor:
                  selectedSession &&
                  selectedSession.session_id === session.session_id
                    ? "#2d2d2d"
                    : "transparent",
                fontSize: "14px",
                color: "#ccc",
                transition: "background-color 0.2s ease",
                position: "relative",
                group: true,
              }}
              onMouseOver={(e) => {
                if (
                  !(
                    selectedSession &&
                    selectedSession.session_id === session.session_id
                  )
                ) {
                  e.currentTarget.style.backgroundColor = "#2a2a2a";
                }
                const deleteBtn =
                  e.currentTarget.querySelector(".delete-btn");
                if (deleteBtn && !collapsed) {
                  deleteBtn.style.opacity = "1";
                }
              }}
              onMouseOut={(e) => {
                if (
                  !(
                    selectedSession &&
                    selectedSession.session_id === session.session_id
                  )
                ) {
                  e.currentTarget.style.backgroundColor = "transparent";
                }
                const deleteBtn =
                  e.currentTarget.querySelector(".delete-btn");
                if (deleteBtn) {
                  deleteBtn.style.opacity = "0";
                }
              }}
            >
              <div
                onClick={() => onSelectSession(session)}
                style={{
                  flex: 1,
                  cursor: "pointer",
                  whiteSpace: "nowrap",
                  overflow: "hidden",
                  textOverflow: "ellipsis",
                  paddingRight: collapsed ? "0" : "8px",
                }}
              >
                <div
                  style={{
                    fontSize: "12px",
                    color: "#888",
                    marginBottom: "2px",
                    display: "flex",
                    alignItems: "center",
                    gap: "4px",
                  }}
                >
                  <span>💬</span>
                  <span>{session.message_count} messages</span>
                </div>
                {collapsed ? (
                  <div style={{ fontSize: "16px", textAlign: "center" }}>
                    💬
                  </div>
                ) : (
                  session.session_title
                )}
              </div>
              {!collapsed && (
                <button
                  className="delete-btn"
                  onClick={(e) => {
                    e.stopPropagation();
                    onDeleteSession(session.session_id);
                  }}
                  style={{
                    background: "transparent",
                    border: "none",
                    color: "#dc2626",
                    fontSize: "14px",
                    cursor: "pointer",
                    padding: "4px",
                    borderRadius: "3px",
                    opacity: "0",
                    transition: "all 0.2s ease",
                    minWidth: "24px",
                    height: "24px",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                  }}
                  onMouseEnter={(e) => {
                    e.target.style.backgroundColor = "#dc2626";
                    e.target.style.color = "white";
                  }}
                  onMouseLeave={(e) => {
                    e.target.style.backgroundColor = "transparent";
                    e.target.style.color = "#dc2626";
                  }}
                  title="Delete this conversation"
                >
                  ×
                </button>
              )}
            </div>
          ))
        )}
      </div>
    </div>
  );
}

export default Sidebar;
