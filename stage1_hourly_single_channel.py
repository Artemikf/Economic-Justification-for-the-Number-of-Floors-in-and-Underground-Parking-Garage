import numpy as np


def get_lambda(day_of_week: int, hour: int) -> float:
    """
    Расписание интенсивности потока lambda(t) [машин/час].
    day_of_week: 0..4 (Пн-Пт), 5..6 (Сб-Вс)
    hour: 0..23
    """
    # Паркинг закрыт с 23:00 до 07:00
    if hour < 7 or hour >= 23:
        return 0.0

    # Будни (Пн-Пт)
    if day_of_week < 5:
        if 8 <= hour < 11:
            return 40.0  # Утренний пик
        elif 11 <= hour < 17:
            return 20.0  # Дневная норма
        elif 17 <= hour < 20:
            return 35.0  # Вечерний пик
        else:
            return 8.0  # Утро/вечер (7-8, 20-23)
    # Выходные (Сб-Вс)
    else:
        if 12 <= hour < 19:
            return 30.0  # Дневной пик ТРЦ
        else:
            return 12.0  # Остальное время


class HourlySingleChannelParking:

    def __init__(self, avg_parking_time: float = 2.0):
        self.avg_parking_time = avg_parking_time

    def run_week_simulation(self):
        current_time = 0.0  # Время в часах от начала недели (0..167)
        busy_until = 0.0  # До какого момента занято место

        total_arrivals = 0
        total_served = 0
        total_rejected = 0

        # Почасовая статистика
        hourly_stats = []

        # 7 дней * 24 часа = 168 часов
        for hour_of_week in range(168):
            day = hour_of_week // 24
            hour_of_day = hour_of_week % 24
            lam = get_lambda(day, hour_of_day)

            hour_arrivals = 0
            hour_served = 0
            hour_rejected = 0

            if lam > 0:
                # Генерируем количество приехавших машин за этот 1 час (Распределение Пуассона)
                vehicles_this_hour = np.random.poisson(lam)
                hour_arrivals = vehicles_this_hour

                # Распределяем заезд машин внутри этого часа
                for _ in range(vehicles_this_hour):
                    # Точное время приезда машины внутри текущего часа
                    arrival_time = current_time + np.random.uniform(0.0, 1.0)

                    # Освобождение места, если время прошло
                    if arrival_time >= busy_until:
                        hour_served += 1
                        # Задаем время стоянки (Exp(mu = 0.5))
                        stay_duration = np.random.exponential(
                            self.avg_parking_time
                        )
                        busy_until = arrival_time + stay_duration
                    else:
                        hour_rejected += 1

            total_arrivals += hour_arrivals
            total_served += hour_served
            total_rejected += hour_rejected

            hourly_stats.append(
                {
                    "hour_global": hour_of_week,
                    "day": day,
                    "hour_day": hour_of_day,
                    "arrivals": hour_arrivals,
                    "served": hour_served,
                    "rejected": hour_rejected,
                }
            )

            current_time += 1.0  # Крок модельного часу = 1 година

        return {
            "total_arrivals": total_arrivals,
            "total_served": total_served,
            "total_rejected": total_rejected,
            "hourly_stats": hourly_stats,
        }


if __name__ == "__main__":
    sim = HourlySingleChannelParking(avg_parking_time=2.0)
    res = sim.run_week_simulation()

    print("=== ИТОГИ ЭТАПА 1: 1 КАНАЛ / 1 НЕДЕЛЯ (168 ЧАСОВ) ===")
    print(f"Всего приехало машин за неделю: {res['total_arrivals']}")
    print(f"Обслужено (1 место):           {res['total_served']}")
    print(f"Уехало из-за отсутствия мест:  {res['total_rejected']}")
    reject_rate = (
        (res["total_rejected"] / res["total_arrivals"] * 100)
        if res["total_arrivals"] > 0
        else 0
    )
    print(f"Процент отказов для 1 места:    {reject_rate:.2f}%")