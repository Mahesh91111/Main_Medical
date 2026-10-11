import { useState } from "react";
import {
  BookOpen,
  ExternalLink,
  FileText,
  Microscope,
  Search,
  ShieldCheck,
} from "lucide-react";

import { searchMedicalResearch } from "../api/research";
import CitationList from "../api/CitationList";

function getResearchError(error) {
  if (error.response?.status === 401) {
    return "Your session has expired. Please sign in again.";
  }

  if (error.response?.status === 403) {
    return "You do not have permission to access this research service.";
  }

  if (error.response?.status === 422) {
    return (
      error.response?.data?.detail ||
      "The research request did not match the backend schema."
    );
  }

  if (!error.response) {
    return "Cannot reach the backend. Check that FastAPI is running.";
  }

  return (
    error.response?.data?.detail ||
    error.response?.data?.message ||
    "The research query failed. Please try again."
  );
}

function getResearchAnswer(data) {
  const value =
    data?.answer ??
    data?.response ??
    data?.summary ??
    data?.output;

  return typeof value === "string" ? value : "";
}

function getSources(data) {
  const value =
    data?.citations ??
    data?.sources ??
    data?.references ??
    [];

  return Array.isArray(value) ? value : [];
}

function getResults(data) {
  const value =
    data?.results ??
    data?.papers ??
    data?.documents ??
    [];

  return Array.isArray(value) ? value : [];
}

export default function Research() {
  const [query, setQuery] = useState("");
  const [answer, setAnswer] = useState("");
  const [sources, setSources] = useState([]);
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [hasSearched, setHasSearched] = useState(false);

  async function handleSearch(event) {
    event.preventDefault();

    const searchQuery = query.trim();

    if (!searchQuery || loading) return;

    setLoading(true);
    setError("");
    setAnswer("");
    setSources([]);
    setResults([]);
    setHasSearched(true);

    try {
      const data = await searchMedicalResearch(searchQuery);

      setAnswer(getResearchAnswer(data));
      setSources(getSources(data));
      setResults(getResults(data));
    } catch (requestError) {
      setError(getResearchError(requestError));
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="workspace-page research-page">
      <div className="workspace-page-heading">
        <div>
          <div className="eyebrow">
            <Microscope size={14} /> EVIDENCE EXPLORATION
          </div>

          <h1>Medical Research</h1>

          <p>
            Explore medical evidence and review the sources returned
            by your connected research service.
          </p>
        </div>
      </div>

      <section className="research-search-panel">
        <div className="research-search-title">
          <div className="research-icon">
            <BookOpen size={22} />
          </div>

          <div>
            <h2>Research a clinical question</h2>
            <p>
              Use a focused question to help retrieve relevant evidence.
            </p>
          </div>
        </div>

        <form
          className="research-search-form"
          onSubmit={handleSearch}
        >
          <label htmlFor="research-query">
            Research question
          </label>

          <textarea
            id="research-query"
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder="Example: What does recent evidence say about the diagnostic accuracy of a particular test?"
            rows={4}
            maxLength={5000}
            disabled={loading}
            required
          />

          <div className="research-search-footer">
            <span>Be specific about the population, intervention, or outcome.</span>

            <button
              type="submit"
              className="primary-button"
              disabled={loading || !query.trim()}
            >
              {loading ? (
                <>
                  <span className="button-spinner" />
                  Searching...
                </>
              ) : (
                <>
                  <Search size={16} />
                  Search evidence
                </>
              )}
            </button>
          </div>
        </form>

        <div className="research-topic-list">
          <span>Try a topic:</span>

          {[
            "Diagnostic accuracy",
            "Clinical trial outcomes",
            "Systematic reviews",
          ].map((topic) => (
            <button
              type="button"
              key={topic}
              onClick={() =>
                setQuery(
                  `Summarize the available medical evidence on ${topic.toLowerCase()}, including relevant limitations and sources.`
                )
              }
              disabled={loading}
            >
              {topic}
            </button>
          ))}
        </div>
      </section>

      {error && (
        <div className="research-error" role="alert">
          <strong>Research request failed</strong>
          <p>{error}</p>
          <button
            type="button"
            onClick={handleSearchFromButton}
            disabled={loading || !query.trim()}
          >
            Try again
          </button>
        </div>
      )}

      {loading && (
        <section className="research-loading" role="status">
          <span className="research-loading-spinner" />
          <div>
            <strong>Searching the available evidence</strong>
            <p>
              Waiting for the research service to return results...
            </p>
          </div>
        </section>
      )}

      {!loading && hasSearched && !error && (
        <section className="research-results">
          <div className="research-results-header">
            <div>
              <div className="eyebrow">QUERY RESULTS</div>
              <h2>Research findings</h2>
            </div>

            <span className="research-result-count">
              {results.length}{" "}
              {results.length === 1 ? "result" : "results"}
            </span>
          </div>

          {answer && (
            <article className="research-answer-card">
              <div className="research-card-heading">
                <BookOpen size={18} />
                <h3>Summary</h3>
              </div>
              <p className="research-answer-text">{answer}</p>
            </article>
          )}

          {results.map((result, index) => {
            const title =
              result.title ||
              result.name ||
              result.filename ||
              `Research result ${index + 1}`;

            const description =
              result.abstract ||
              result.summary ||
              result.excerpt ||
              result.snippet ||
              result.content;

            const url = result.url || result.source_url;
            const id =
              result.id ||
              result.url ||
              result.title ||
              `result-${index}`;

            return (
              <article
                className="research-result-card"
                key={id}
              >
                <div className="research-result-icon">
                  <FileText size={18} />
                </div>

                <div className="research-result-body">
                  <h3>{title}</h3>

                  {description && (
                    <p>
                      {String(description).slice(0, 1500)}
                    </p>
                  )}

                  <div className="research-result-meta">
                    {result.year && <span>{result.year}</span>}
                    {result.journal && <span>{result.journal}</span>}
                    {result.authors && (
                      <span>
                        {Array.isArray(result.authors)
                          ? result.authors.join(", ")
                          : result.authors}
                      </span>
                    )}
                  </div>

                  {url && (
                    <a
                      href={url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="research-source-link"
                    >
                      Open source <ExternalLink size={14} />
                    </a>
                  )}
                </div>
              </article>
            );
          })}

          {sources.length > 0 && (
            <article className="research-answer-card">
              <div className="research-card-heading">
                <BookOpen size={18} />
                <h3>Supporting sources</h3>
              </div>

              <CitationList citations={sources} />
            </article>
          )}

          {!answer && results.length === 0 && sources.length === 0 && (
            <div className="research-empty-results">
              <BookOpen size={24} />
              <h3>No results returned</h3>
              <p>
                Try a more specific question, or check whether the
                backend returned the expected response fields.
              </p>
            </div>
          )}
        </section>
      )}

      {!hasSearched && (
        <div className="research-empty-state">
          <div className="research-empty-state-icon">
            <Microscope size={24} />
          </div>
          <h2>Your research results will appear here</h2>
          <p>
            Submit a question to view findings, abstracts, and citations
            provided by the backend.
          </p>
        </div>
      )}

      <div className="research-disclaimer">
        <ShieldCheck size={16} />
        <p>
          Research summaries are aids for evidence exploration, not a
          substitute for reading source publications or evaluating
          study quality, relevance, and limitations.
        </p>
      </div>
    </div>
  );

  function handleSearchFromButton() {
    handleSearch({
      preventDefault() {},
    });
  }
}