import { useRouter } from 'next/router';
import useSWR from 'swr';
import { Line } from 'react-chartjs-2';
import { Chart as ChartJS, LineElement, PointElement, LinearScale, TimeScale, Title, Tooltip, Legend } from 'chart.js';
import 'chartjs-adapter-date-fns';

ChartJS.register(LineElement, PointElement, LinearScale, TimeScale, Title, Tooltip, Legend);

const fetcher = url => fetch(url).then(r => r.json());

export default function HistoryPage() {
  const router = useRouter();
  const { id } = router.query;
  const { data, error } = useSWR(id ? `/api/history?id=${id}` : null, fetcher);

  if (error) return <div className="p-8">Eroare la încărcare.</div>;
  if (!data) return <div className="p-8">Se încarcă...</div>;

  const chartData = {
    labels: data.map(d => new Date(d.created_at)),
    datasets: [
      {
        label: 'Preț (RON)',
        data: data.map(d => d.price_cents / 100),
        borderColor: 'blue',
        fill: false
      }
    ]
  };

  const chartOptions = {
    responsive: true,
    scales: {
      x: { type: 'time', time: { unit: 'day' } }
    }
  };

  return (
    <div className="p-8">
      <h1 className="text-2xl mb-4 font-bold">Istoric preț</h1>
      <Line data={chartData} options={chartOptions} />
    </div>
  );
}
