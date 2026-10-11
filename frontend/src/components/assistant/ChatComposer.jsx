import { Send } from "lucide-react";

export default function ChatComposer({
  value,
  onChange,
  onSubmit,
  loading,
  disabled = false,
}) {
  function handleSubmit(event) {
    event.preventDefault();

    if (!loading && !disabled && value.trim()) {
      onSubmit();
    }
  }

  return (
    <form className="chat-composer" onSubmit={handleSubmit}>
      <textarea
        value={value}
        onChange={(event) => onChange(event.target.value)}
        placeholder="Ask a medical or clinical information question..."
        aria-label="Your question"
        rows={2}
        maxLength={5000}
        disabled={loading || disabled}
        onKeyDown={(event) => {
          if (
            event.key === "Enter" &&
            !event.shiftKey &&
            !event.nativeEvent.isComposing
          ) {
            event.preventDefault();
            event.currentTarget.form?.requestSubmit();
          }
        }}
      />

      <div className="chat-composer-footer">
        <span>Enter to send · Shift + Enter for a new line</span>

        <button
          type="submit"
          className="primary-button chat-send-button"
          disabled={loading || disabled || !value.trim()}
        >
          {loading ? (
            <>
              <span className="button-spinner" />
              Thinking
            </>
          ) : (
            <>
              Send <Send size={15} />
            </>
          )}
        </button>
      </div>
    </form>
  );
}