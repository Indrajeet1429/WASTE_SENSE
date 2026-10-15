import { Link } from "react-router-dom";

export default function Logo() {
  return (
    <Link className="logo" to="/" aria-label="WasteSense home">
      <span className="lm"><img src="/logo-mark.jpg" alt="" /></span>
      <b className="wm">Waste<span>Sense</span></b>
    </Link>
  );
}
