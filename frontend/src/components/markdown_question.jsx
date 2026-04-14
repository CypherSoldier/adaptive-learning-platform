import MarkdownRenderer from "./markdown_renderer";

export default function Question({ question }) {
  return (
    <div>
      <MarkdownRenderer content={question} />
    </div>
  );
}