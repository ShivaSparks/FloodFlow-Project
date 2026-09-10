type Props = {
  label: string;
  value: string;
  detail: string;
  tone?: "blue" | "orange" | "red" | "green";
};

export default function StatCard({ label, value, detail, tone = "blue" }: Props) {
  return (
    <div className={`stat-card stat-${tone}`}>
      <span>{label}</span>
      <strong>{value}</strong>
      <small>{detail}</small>
    </div>
  );
}
