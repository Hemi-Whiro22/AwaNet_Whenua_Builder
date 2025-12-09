export default function ChatMessage({ role, content }) {
  const isUser = role === "user";
  const renderContent = () => {
    if (typeof content !== "string") return <div className="whitespace-pre-wrap break-words">{content}</div>;
    const linkified = content.replace(
      /(https?:\/\/[^\s]+)/g,
      '<a href="$1" target="_blank" rel="noreferrer" class="underline text-koru1 hover:text-koru2 break-words">$1</a>'
    );
    return <div className="whitespace-pre-wrap break-words" dangerouslySetInnerHTML={{ __html: linkified }} />;
  };
  return (
    <div className={`max-w-[80%] py-2 px-4 rounded-xl shadow ${isUser ? "bg-koru1 text-black ml-auto" : "bg-panel/60 text-koru1"}`}>
      {renderContent()}
    </div>
  );
}
