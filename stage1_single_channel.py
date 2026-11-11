import numpy as np


class SingleChannelParkingSimulator:

    def __init__(self, arrival_rate_lambda: float, avg_parking_time: float):
        """
        arrival_rate_lambda: интенсивность прибытия машин (авто в час)
        avg_parking_time: среднее время парковки (в часах), по условию 2 часа
        """
        self.lambda_rate = arrival_rate_lambda
        self.mu_rate = 1.0 / avg_parking_time  # mu = 0.5

    def generate_interarrival_time(self) -> float:
        """Генерация интервала времени до прибытия следующей машины (Exp(lambda))"""
        return np.random.exponential(1.0 / self.lambda_rate)

    def generate_parking_duration(self) -> float:
        """Генерация времени стоянки машины (Exp(mu))"""
        return np.random.exponential(1.0 / self.mu_rate)

    def run_simulation(self, total_vehicles: int = 50000):
        """Симуляция работы 1 места для N приехавших машин"""
        current_time = 0.0
        channel_busy_until = 0.0

        served_count = 0
        rejected_count = 0
        total_busy_time = 0.0

        for _ in range(total_vehicles):
            # Время приезда следующего авто
            interarrival = self.generate_interarrival_time()
            current_time += interarrival

            # Проверяем свободность 1 канала
            if current_time >= channel_busy_until:
                # Место свободно -> заезд
                served_count += 1
                duration = self.generate_parking_duration()
                channel_busy_until = current_time + duration
                total_busy_time += duration
            else:
                # Место занято -> отказ
                rejected_count += 1

        empirical_p_reject = rejected_count / total_vehicles
        return {
            "total_vehicles": total_vehicles,
            "served": served_count,
            "rejected": rejected_count,
            "empirical_p_reject": empirical_p_reject,
        }


# --- Запуск теста и сравнение с теорией ---
if __name__ == "__main__":
    LAMBDA_TEST = 1.0  # 1 машина в час
    AVG_STAY = 2.0  # 2 часа средняя парковка

    sim = SingleChannelParkingSimulator(
        arrival_rate_lambda=LAMBDA_TEST, avg_parking_time=AVG_STAY
    )
    results = sim.run_simulation(total_vehicles=100000)

    # Теоретический расчет
    rho = LAMBDA_TEST / (1.0 / AVG_STAY)  # rho = 1.0 / 0.5 = 2.0
    theoretical_p_reject = rho / (1.0 + rho)  # 2 / 3 = 0.6667

    print("=== РЕЗУЛЬТАТЫ ЕТАПА 1 (1 КАНАЛ) ===")
    print(f"Всего автомобилей: {results['total_vehicles']}")
    print(f"Обслужено: {results['served']}")
    print(f"Отказов (уехали): {results['rejected']}")
    print(f"Эмпирический % отказов (Симуляция): {results['empirical_p_reject']:.4f}")
    print(f"Теоретический % отказов (Эрланг):   {theoretical_p_reject:.4f}")