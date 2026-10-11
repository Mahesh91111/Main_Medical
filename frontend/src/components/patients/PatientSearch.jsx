
import { Search, X } from "lucide-react";

export default function PatientSearch({
  query,
  onQueryChange,
  gender,
  onGenderChange
}) {
  return (
    <div className="patient-search-toolbar">
      <div className="patient-search-input">
        <Search size={18} aria-hidden="true" />

        <input
          type="search"
          placeholder="Search by patient name, email, or ID..."
          value={query}
          onChange={(event) => onQueryChange(event.target.value)}
          aria-label="Search patients"
        />

        {query && (
          <button
            type="button"
            className="search-clear"
            onClick={() => onQueryChange("")}
            aria-label="Clear search"
          >
            <X size={16} />
          </button>
        )}
      </div>

      <select
        className="patient-gender-filter"
        value={gender}
        onChange={(event) => onGenderChange(event.target.value)}
        aria-label="Filter by gender"
      >
        <option value="">All genders</option>
        <option value="female">Female</option>
        <option value="male">Male</option>
        <option value="other">Other</option>
        <option value="unknown">Unknown / not specified</option>
      </select>
    </div>
  );
}
