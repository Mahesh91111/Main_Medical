import { ExternalLink, BookOpen } from "lucide-react";

function getCitationKey(citation, index) {
  if (typeof citation === "string") return `${citation}-${index}`;

  return (
    citation.id ||
    citation.url ||
    citation.source ||
    citation.title ||
    `citation-${index}`
  );
}

export default function CitationList({ citations = [] }) {
  if (!Array.isArray(citations) || citations.length === 0) {
    return null;
  }

  return (
    <section className="citation-section" aria-label="Sources and citations">
      <div className="citation-heading">
        <BookOpen size={16} />
        <span>Sources</span>
        <span className="citation-count">{citations.length}</span>
      </div>

      <div className="citation-list">
        {citations.map((citation, index) => {
          const item =
            typeof citation === "string"
              ? { title: citation }
              : citation || {};

          const title =
            item.title ||
            item.filename ||
            item.source ||
            item.document_name ||
            `Source ${index + 1}`;

          const url = item.url || item.source_url;
          const excerpt =
            item.excerpt ||
            item.snippet ||
            item.content ||
            item.page_content;

          return (
            <article
              className="citation-item"
              key={getCitationKey(citation, index)}
            >
              <div className="citation-item-title">
                <span>{index + 1}.</span>

                {url ? (
                  <a
                    href={url}
                    target="_blank"
                    rel="noopener noreferrer"
                  >
                    {title}
                    <ExternalLink size={13} />
                  </a>
                ) : (
                  <span>{title}</span>
                )}
              </div>

              {item.page != null && (
                <p className="citation-page">
                  Page {item.page}
                </p>
              )}

              {excerpt && (
                <p className="citation-excerpt">
                  {String(excerpt).slice(0, 500)}
                </p>
              )}
            </article>
          );
        })}
      </div>
    </section>
  );
}