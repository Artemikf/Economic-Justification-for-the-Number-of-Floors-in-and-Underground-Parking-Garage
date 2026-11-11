import csv
import numpy as np


def get_lambda(day_of_week: int, hour: int) -> float:
    """Расписание интенсивности потока lambda(t) [машин/час]."""
    if hour < 7 or hour >= 23:
        return 0.0

    if day_of_week < 5:  # Будни
        if 8 <= hour < 11:
            return 40.0
        elif 11 <= hour < 17:
            return 20.0
        elif 17 <= hour < 20:
            return 35.0
        else:
            return 8.0
    else:  # Выходные
        if 12 <= hour < 19:
            return 30.0
        else:
            return 12.0


class ParkingMonteCarloSimulator:

    def __init__(
        self,
        c_per_floor: int = 40,
        avg_parking_time: float = 2.0,
        hourly_rate: float = 40.0,
        floor_monthly_cost: float = 50000.0,
    ):
        self.c_per_floor = c_per_floor
        self.avg_parking_time = avg_parking_time
        self.hourly_rate = hourly_rate
        self.floor_monthly_cost = floor_monthly_cost

    def _simulate_single_week(self, K_floors: int):
        """Симуляция одной недели (168 часов)."""
        total_capacity = K_floors * self.c_per_floor
        occupied_until = []

        total_arrivals = 0
        total_served = 0
        total_rejected = 0
        total_paid_hours = 0.0

        current_time = 0.0

        for hour_of_week in range(168):
            day = hour_of_week // 24
            hour_of_day = hour_of_week % 24
            lam = get_lambda(day, hour_of_day)

            if lam > 0:
                vehicles_count = np.random.poisson(lam)
                total_arrivals += vehicles_count

                arrival_offsets = np.sort(
                    np.random.uniform(0.0, 1.0, size=vehicles_count)
                )

                for offset in arrival_offsets:
                    arr_time = current_time + offset
                    occupied_until = [t for t in occupied_until if t > arr_time]

                    if len(occupied_until) < total_capacity:
                        total_served += 1
                        stay_duration = np.random.exponential(
                            self.avg_parking_time
                        )
                        occupied_until.append(arr_time + stay_duration)
                        total_paid_hours += stay_duration
                    else:
                        total_rejected += 1

            current_time += 1.0

        return total_arrivals, total_served, total_rejected, total_paid_hours

    def run_monte_carlo(self, K_floors: int, num_runs: int = 50):
        """Прогон N недель и усреднение показателей."""
        arrivals_list = []
        served_list = []
        rejected_list = []
        paid_hours_list = []

        for _ in range(num_runs):
            arr, serv, rej, hours = self._simulate_single_week(K_floors)
            arrivals_list.append(arr)
            served_list.append(serv)
            rejected_list.append(rej)
            paid_hours_list.append(hours)

        avg_arrivals = np.mean(arrivals_list)
        avg_served = np.mean(served_list)
        avg_rejected = np.mean(rejected_list)
        avg_paid_hours = np.mean(paid_hours_list)

        weekly_revenue = avg_paid_hours * self.hourly_rate
        monthly_revenue = weekly_revenue * 4.33
        monthly_expenses = K_floors * self.floor_monthly_cost
        monthly_net_profit = monthly_revenue - monthly_expenses
        reject_percentage = (
            (avg_rejected / avg_arrivals * 100) if avg_arrivals > 0 else 0.0
        )

        return {
            "K_floors": K_floors,
            "total_capacity": K_floors * self.c_per_floor,
            "avg_arrivals": round(avg_arrivals, 1),
            "avg_served": round(avg_served, 1),
            "avg_rejected": round(avg_rejected, 1),
            "reject_percentage": round(reject_percentage, 2),
            "monthly_revenue": round(monthly_revenue, 2),
            "monthly_expenses": round(monthly_expenses, 2),
            "monthly_net_profit": round(monthly_net_profit, 2),
        }


if __name__ == "__main__":
    sim = ParkingMonteCarloSimulator(
        c_per_floor=40,
        avg_parking_time=2.0,
        hourly_rate=40.0,
        floor_monthly_cost=50000.0,
    )

    results = []
    print("Выполнение Монте-Карло симуляции (50 недель на каждый этаж)...")

    for k in range(1, 11):
        res = sim.run_monte_carlo(K_floors=k, num_runs=50)
        results.append(res)
        print(
            f"Этажи: {k:2d} | Ср. Отказы: {res['reject_percentage']:6.2f}% | Чистая прибыль: {res['monthly_net_profit']:12.2f} грн"
        )

    # Сохранение результатов в CSV файл для напарника
    csv_file = "simulation_results.csv"
    fieldnames = list(results[0].keys())

    with open(csv_file, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    print(f"\n Результаты успешно сохранены в файл '{csv_file}'!")