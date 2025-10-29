export default function Loader({ label = "Working..." }: { label?: string }) {
  return (
    <div style={{
      display: "flex",
      gap: 12,
      alignItems: "center",
      justifyContent: "center",
      padding: "16px 0"
    }}>
      <div className="spinner" />
      <span>{label}</span>
    </div>
  );
}