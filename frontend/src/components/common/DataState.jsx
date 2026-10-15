import Note from "./Note";

// Renders loading and error states, then calls children(data) once data is ready.
export default function DataState({ state, children }) {
  if (state.loading && !state.data) return <div className="state">Loading data...</div>;
  if (state.error) return <Note>Could not load data ({state.error}). Check the API connection and try again.</Note>;
  return state.data === null || state.data === undefined ? null : <>{children(state.data)}</>;
}
