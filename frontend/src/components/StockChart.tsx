import React, { useEffect, useState } from 'react';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

interface StockData {
  date: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

interface StockChartProps {
  data: StockData[];
  title: string;
  symbol: string;
}

/**
 * 股票价格图表组件
 */
const StockChart: React.FC<StockChartProps> = ({ data, title, symbol }) => {
  const [chartData, setChartData] = useState<any>(null);

  useEffect(() => {
    if (!data || data.length === 0) return;

    const labels = data.map(d => d.date);
    const prices = data.map(d => d.close);
    const ma5 = calculateMA(prices, 5);
    const ma20 = calculateMA(prices, 20);

    setChartData({
      labels,
      datasets: [
        {
          label: '收盘价',
          data: prices,
          borderColor: '#3B82F6',
          backgroundColor: 'rgba(59, 130, 246, 0.1)',
          borderWidth: 2,
          tension: 0.1,
        },
        {
          label: 'MA5',
          data: ma5,
          borderColor: '#F59E0B',
          borderWidth: 1,
          tension: 0.1,
        },
        {
          label: 'MA20',
          data: ma20,
          borderColor: '#EF4444',
          borderWidth: 1,
          tension: 0.1,
        },
      ],
    });
  }, [data]);

  const calculateMA = (prices: number[], period: number) => {
    return prices.map((_, index) => {
      if (index < period - 1) return null;
      const sum = prices.slice(index - period + 1, index + 1).reduce((a, b) => a + b, 0);
      return sum / period;
    });
  };

  if (!chartData) {
    return <div className="flex items-center justify-center h-64 text-gray-500">加载中...</div>;
  }

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h3 className="text-lg font-semibold mb-4">{title} ({symbol})</h3>
      <div style={{ position: 'relative', height: '300px' }}>
        <Line
          data={chartData}
          options={{
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
              legend: {
                display: true,
                position: 'top',
              },
            },
            scales: {
              y: {
                beginAtZero: false,
              },
            },
          }}
        />
      </div>
    </div>
  );
};

export default StockChart;
