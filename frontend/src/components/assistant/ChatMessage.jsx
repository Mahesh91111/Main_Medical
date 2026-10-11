import { Bot, UserRound } from "lucide-react";
import CitationList from "../../api/CitationList";

export default function ChatMessage({ message }) {
  const isAssistant = message.role === "assistant";

  return (
    <article
      className={`chat-message ${
        isAssistant ? "assistant-message" : "user-message"
      }`}
    >
      <div className="chat-message-avatar">
        {isAssistant ? (
          <Bot size={18} />
        ) : (
          <UserRound size={18} />
        )}
      </div>

      <div className="chat-message-content">
        <div className="chat-message-meta">
          <strong>{isAssistant ? "Clinica AI" : "You"}</strong>
          {message.time && <span>{message.time}</span>}
        </div>

        <div className="chat-message-bubble">
          <p className="chat-message-text">
            {message.content}
          </p>
        </div>

        {isAssistant && (
          <CitationList citations={message.citations || []} />
        )}
      </div>
    </article>
  );
}