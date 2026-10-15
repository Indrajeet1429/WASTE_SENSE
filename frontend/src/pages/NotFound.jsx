import { Link } from "react-router-dom";

export default function NotFound() {
  return (
    <div className="state">
      <h2>Page not found</h2>
      <p>That address does not exist. <Link to="/">Go to the home page</Link>.</p>
    </div>
  );
}
