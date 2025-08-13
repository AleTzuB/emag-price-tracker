import { Pool } from "pg";

export async function getServerSideProps() {
  const pool = new Pool({
    connectionString: process.env.POSTGRES_URL, // variabila de mediu din Vercel
    ssl: { rejectUnauthorized: false }
  });

  const client = await pool.connect();
  const result = await client.query(`
    SELECT p.id, p.name, p.url, ph.price, ph.checked_at
    FROM products p
    JOIN LATERAL (
      SELECT price, checked_at
      FROM price_history
      WHERE product_id = p.id
      ORDER BY checked_at DESC
      LIMIT 1
    ) ph ON true
    ORDER BY p.id;
  `);

  client.release();

  return {
    props: {
      products: result.rows.map(row => ({
        id: row.id,
        name: row.name,
        url: row.url,
        price: Number(row.price),
        checked_at: row.checked_at.toString()
      }))
    }
  };
}

export default function Home({ products }) {
  return (
    <div style={{ padding: "20px", fontFamily: "Arial, sans-serif" }}>
      <h1>eMAG Price Tracker</h1>
      <table border="1" cellPadding="8" style={{ borderCollapse: "collapse", width: "100%" }}>
        <thead>
          <tr>
            <th>Produs</th>
            <th>Preț (RON)</th>
            <th>Ultima verificare</th>
            <th>Link</th>
          </tr>
        </thead>
        <tbody>
          {products.map(prod => (
            <tr key={prod.id}>
              <td>{prod.name}</td>
              <td>{prod.price.toFixed(2)}</td>
              <td>{new Date(prod.checked_at).toLocaleString()}</td>
              <td><a href={prod.url} target="_blank" rel="noopener noreferrer">Vezi</a></td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
