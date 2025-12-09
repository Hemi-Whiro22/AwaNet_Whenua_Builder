export default function ToolResultCard({ title, content }) {
  const renderContent = () => {
    if (typeof content !== "string") return <div className="whitespace-pre-wrap break-words text-koru2 text-sm">{content}</div>;
    const linkified = content.replace(
      /(https?:\/\/[^\s]+)/g,
      '<a href="$1" target="_blank" rel="noreferrer" class="underline text-koru1 hover:text-koru2 break-words">$1</a>'
    );
    return <div className="mt-2 text-koru2 text-sm whitespace-pre-wrap break-words" dangerouslySetInnerHTML={{ __html: linkified }} />;
  };
  return (
    <div className="rounded-xl border border-border bg-panel/60 p-4 shadow">
      <p className="text-koru1 font-semibold text-sm">{title}</p>
      {renderContent()}
    </div>
  );
}
