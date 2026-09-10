import type { ReactNode } from "react";

type Props = { eyebrow: string; title: string; description: string; children?: ReactNode };

export default function SimplePage({ eyebrow, title, description, children }: Props) {
  return <section className="dashboard-page simple-page"><p className="eyebrow">{eyebrow}</p><h1>{title}</h1><p className="muted wide-copy">{description}</p><div className="placeholder-card">{children ?? <><span className="placeholder-icon">◌</span><h3>Module ready for integration</h3><p>This view will connect to the Stage 4 API and display live prototype data.</p></>}</div></section>;
}
