import numpy as np


def get_lambda(day_of_week: int, hour: int) -> float:
    """Расписание интенсивности потока lambda(t) [машин/час]."""
    if hour < 7 or hour >= 23:
        return 0.0

    # Будни (Пн-Пт)
    if day_of_week < 5:
        if 8 <= hour < 11:
            return 40.0
        elif 11 <= hour < 17:
            return 20.0
        elif 17 <= hour < 20:
            return 35.0
        else:
            return 8.0
    # Выходные (Сб-Вс)
    else:
        if 12 <= hour < 19:
            return 30.0
        else:
            return 12.0


class MultiChannelParkingSimulator:

    def __init__(
        self,
        c_per_floor: int = 40,
        avg_parking_time: float = 2.0,
        hourly_rate: float = 40.0,
        floor_monthly_cost: float = 50000.0,
    ):
        """
        c_per_floor: вместимость 1 этажа (машиномест)
        avg_parking_time: среднее время стоянки (часы)
        hourly_rate: тариф за 1 час парковки (грн)
        floor_monthly_cost: стоимость содержания 1 этажа в месяц (грн)
        """
        self.c_per_floor = c_per_floor
        self.avg_parking_time = avg_parking_time
        self.hourly_rate = hourly_rate
        self.floor_monthly_cost = floor_monthly_cost

    def simulate_week_for_floors(self, K_floors: int):
        """Симуляция 1 недели (168 часов) для K этажей."""
        total_capacity = K_floors * self.c_per_floor

        # Массив времен выезда активных автомобилей
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

                # Сортируем прибытия автомобилей внутри текущего часа
                arrival_offsets = np.sort(np.random.uniform(0.0, 1.0, size=vehicles_count))

                for offset in arrival_offsets:
                    arr_time = current_time + offset

                    # Освобождаем места у выехавших к моменту arr_time машин
                    occupied_until = [t for t in occupied_until if t > arr_time]

                    # Проверяем наличие свободного места
                    if len(occupied_until) < total_capacity:
                        total_served += 1
                        stay_duration = np.random.exponential(self.avg_parking_time)
                        occupied_until.append(arr_time + stay_duration)
                        total_paid_hours += stay_duration
                    else:
                        total_rejected += 1

            current_time += 1.0

        # --- Экономический расчет ---
        # 1 месяц ≈ 4.33 недели
        weekly_revenue = total_paid_hours * self.hourly_rate
        monthly_revenue = weekly_revenue * 4.33
        monthly_expenses = K_floors * self.floor_monthly_cost
        monthly_net_profit = monthly_revenue - monthly_expenses

        reject_percentage = (
            (total_rejected / total_arrivals * 100) if total_arrivals > 0 else 0.0
        )

        return {
            "K_floors": K_floors,
            "total_capacity": total_capacity,
            "total_arrivals": total_arrivals,
            "served": total_served,
            "rejected": total_rejected,
            "reject_percentage": reject_percentage,
            "total_paid_hours": total_paid_hours,
            "monthly_revenue": monthly_revenue,
            "monthly_expenses": monthly_expenses,
            "monthly_net_profit": monthly_net_profit,
        }


# --- ЗАПУСК ПОЛНОГО ЭКСПЕРИМЕНТА (K = 1..10 этажей) ---
if __name__ == "__main__":
    sim = MultiChannelParkingSimulator(
        c_per_floor=40,
        avg_parking_time=2.0,
        hourly_rate=40.0,
        floor_monthly_cost=50000.0,
    )

    results_table = []
    best_k = 1
    max_profit = float("-inf")

    print("=== ЕТАП 2: РЕЗУЛЬТАТИ СИМУЛЯЦІЇ ДЛЯ K = 1..10 ПОВЕРХІВ ===")
    print("-" * 95)
    print(
        f"{'K':<3} | {'Місць':<6} | {'Приїхало':<8} | {'Обслуговано':<11} | {'Відмови %':<10} | "
        f"{'Дохід/міс (грн)':<16} | {'Витрати/міс':<13} | {'Чистий прибуток (грн)'}"
    )
    print("-" * 95)

    for k in range(1, 11):
        res = sim.simulate_week_for_floors(K_floors=k)
        results_table.append(res)

        if res["monthly_net_profit"] > max_profit:
            max_profit = res["monthly_net_profit"]
            best_k = k

        print(
            f"{res['K_floors']:<3} | {res['total_capacity']:<6} | {res['total_arrivals']:<8} | "
            f"{res['served']:<11} | {res['reject_percentage']:<9.2f}% | "
            f"{res['monthly_revenue']:<16.2f} | {res['monthly_expenses']:<13.2f} | "
            f"{res['monthly_net_profit']:<18.2f}"
        )

    print("-" * 95)
    print(f"\n ОПТИМАЛЬНА КІЛЬКІСТЬ ПОВЕРХІВ: K = {best_k}")
    print(f" МАКСИМАЛЬНИЙ ЧИСТИЙ ПРИБУТОК: {max_profit:,.2f} грн/місяць")