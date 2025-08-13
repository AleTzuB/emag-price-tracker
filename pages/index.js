import useSWR from 'swr';
import Link from 'next/link';

const fetcher = url => fetch(url).then(r => r.json());

export default function Home() {
  const { data, error } = useSWR('/api/scrape', fetcher, { refreshInterval: 600000 });

  if (error) return <div className="p-8">Eroare la încărcare.</div>;
  if (!data) return <div className="p-8">Se încarcă...</div>;

  return (
    <div className="p-8">
      <h1 className="text-3xl mb-6 font-bold">eMAG Price Tracker</h1>
      {data.map(p => (
        <div key={p.id} className="border p-4 mb-4 rounded-lg">
          <a href={p.url} target="_blank" rel="noopener noreferrer" className="text-lg font-semibold">{p.name}</a>
          <div className="text-xl mt-2">{p.price ? `${p.price} ${p.currency}` : "Preț indisponibil"}</div>
          <Link href={`/history/${p.id}`} className="text-blue-600 underline mt-2 block">Vezi istoric</Link>
        </div>
      ))}
    </div>
  );
}
