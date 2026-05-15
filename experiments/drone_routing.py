from __future__ import annotations

import argparse
import csv
import math
import random
import re
import time
from dataclasses import dataclass
from pathlib import Path
from statistics import mean


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INSTANCE_DIR = ROOT / "data" / "raw" / "evrptw" / "instances" / "evrptw_instances"
DEFAULT_RESULTS_DIR = ROOT / "results" / "drone_routing_full_small"


@dataclass(frozen=True)
class Node:
    node_id: str
    kind: str
    x: float
    y: float
    demand: float
    ready: float
    due: float
    service: float


@dataclass
class Instance:
    name: str
    depot: Node
    stations: list[Node]
    customers: list[Node]
    params: dict[str, float]


@dataclass(frozen=True)
class DroneParams:
    capacity: float = 50.0
    range_limit: float = 45.0
    speed: float = 1.0
    service_time: float = 5.0
    recharge_fixed_time: float = 8.0
    recharge_time_per_unit: float = 0.15
    tardiness_weight: float = 10.0
    drone_weight: float = 100.0
    infeasible_penalty: float = 1_000_000.0


def distance(a: Node, b: Node) -> float:
    return math.hypot(a.x - b.x, a.y - b.y)


def parse_instance(path: Path) -> Instance:
    nodes: list[Node] = []
    params: dict[str, float] = {}
    lines = path.read_text(encoding="utf-8").splitlines()

    for line in lines[1:]:
        stripped = line.strip()
        if not stripped:
            continue
        if "/" in stripped:
            value = float(re.search(r"/([^/]+)/", stripped).group(1))
            if stripped.startswith("Q "):
                params["battery_capacity"] = value
            elif stripped.startswith("C "):
                params["load_capacity"] = value
            elif stripped.startswith("r "):
                params["consumption_rate"] = value
            elif stripped.startswith("g "):
                params["inverse_refuel_rate"] = value
            elif stripped.startswith("v "):
                params["velocity"] = value
            continue

        parts = stripped.split()
        if len(parts) == 8:
            nodes.append(
                Node(
                    node_id=parts[0],
                    kind=parts[1],
                    x=float(parts[2]),
                    y=float(parts[3]),
                    demand=float(parts[4]),
                    ready=float(parts[5]),
                    due=float(parts[6]),
                    service=float(parts[7]),
                )
            )

    depot = next(n for n in nodes if n.kind == "d")
    stations = [n for n in nodes if n.kind == "f"]
    customers = sorted(
        [n for n in nodes if n.kind == "c"],
        key=lambda n: int(re.sub(r"\D", "", n.node_id) or 0),
    )
    return Instance(path.stem, depot, stations, customers, params)


def active_customers(instance: Instance, period: int, periods: int, scenario: str) -> list[Node]:
    customers = list(instance.customers)
    if scenario == "temporal":
        customers.sort(key=lambda n: (n.ready, n.due, n.node_id))
    elif scenario == "spatial":
        cx, cy = instance.depot.x, instance.depot.y
        customers.sort(key=lambda n: math.atan2(n.y - cy, n.x - cx))
    else:
        customers.sort(key=lambda n: int(re.sub(r"\D", "", n.node_id) or 0))

    count = max(1, math.ceil(len(customers) * period / periods))
    return customers[:count]


def select_stations(instance: Instance, customers: list[Node], period: int, periods: int, policy: str) -> list[Node]:
    depot_stations = [s for s in instance.stations if distance(s, instance.depot) < 1e-9]
    non_depot = [s for s in instance.stations if s not in depot_stations]
    if policy == "all":
        return list(instance.stations)
    if policy == "depot":
        return depot_stations or [instance.depot]

    target = max(1, math.ceil(len(non_depot) * period / periods))
    selected: list[Node] = []
    remaining = list(non_depot)
    while remaining and len(selected) < target:
        best = min(
            remaining,
            key=lambda s: sum(min(distance(c, x) for x in selected + depot_stations + [s]) for c in customers),
        )
        selected.append(best)
        remaining.remove(best)
    return (depot_stations or [instance.depot]) + selected


def split_by_capacity(order: list[Node], params: DroneParams) -> list[list[Node]]:
    routes: list[list[Node]] = []
    current: list[Node] = []
    load = 0.0
    for customer in order:
        if current and load + customer.demand > params.capacity:
            routes.append(current)
            current = []
            load = 0.0
        current.append(customer)
        load += customer.demand
    if current:
        routes.append(current)
    return routes


def route_load(route: list[Node]) -> float:
    return sum(customer.demand for customer in route)


def clean_routes(routes: list[list[Node]]) -> list[list[Node]]:
    return [list(route) for route in routes if route]


def nearest_routes(instance: Instance, customers: list[Node], params: DroneParams) -> list[list[Node]]:
    remaining = set(customers)
    routes: list[list[Node]] = []
    while remaining:
        route: list[Node] = []
        load = 0.0
        current = instance.depot
        while True:
            candidates = [c for c in remaining if load + c.demand <= params.capacity]
            if not candidates:
                break
            nxt = min(candidates, key=lambda c: distance(current, c))
            route.append(nxt)
            remaining.remove(nxt)
            load += nxt.demand
            current = nxt
        routes.append(route)
    return routes


def warm_start_routes(
    instance: Instance,
    previous_routes: list[list[Node]] | None,
    customers: list[Node],
    stations: list[Node],
    params: DroneParams,
) -> list[list[Node]]:
    if not previous_routes:
        return nearest_routes(instance, customers, params)

    active_ids = {customer.node_id for customer in customers}
    routes = clean_routes(
        [[customer for customer in route if customer.node_id in active_ids] for route in previous_routes]
    )
    present_ids = {customer.node_id for route in routes for customer in route}
    missing = [customer for customer in customers if customer.node_id not in present_ids]

    for customer in missing:
        best_candidate: list[list[Node]] | None = None
        best_score = float("inf")
        for ridx, route in enumerate(routes):
            if route_load(route) + customer.demand > params.capacity:
                continue
            for pos in range(len(route) + 1):
                candidate = [list(r) for r in routes]
                candidate[ridx].insert(pos, customer)
                score = evaluate(instance, candidate, stations, params)["objective"]
                if score < best_score:
                    best_candidate = candidate
                    best_score = score

        candidate = [list(r) for r in routes] + [[customer]]
        score = evaluate(instance, candidate, stations, params)["objective"]
        if score < best_score:
            best_candidate = candidate

        routes = clean_routes(best_candidate or candidate)

    return routes


def randomized_nearest_routes(
    instance: Instance, customers: list[Node], params: DroneParams, rng: random.Random
) -> list[list[Node]]:
    remaining = set(customers)
    routes: list[list[Node]] = []
    while remaining:
        route: list[Node] = []
        load = 0.0
        current = instance.depot
        while True:
            candidates = [c for c in remaining if load + c.demand <= params.capacity]
            if not candidates:
                break
            candidates.sort(key=lambda c: distance(current, c))
            pool = candidates[: min(3, len(candidates))]
            nxt = rng.choice(pool)
            route.append(nxt)
            remaining.remove(nxt)
            load += nxt.demand
            current = nxt
        routes.append(route)
    return routes


def build_routes(
    algorithm: str,
    instance: Instance,
    customers: list[Node],
    stations: list[Node],
    params: DroneParams,
    rng: random.Random,
    restarts: int,
    vns_iterations: int,
    warm_start: list[list[Node]] | None = None,
) -> list[list[Node]]:
    if algorithm == "edd":
        order = sorted(customers, key=lambda n: (n.due, n.ready, n.node_id))
        return split_by_capacity(order, params)
    if algorithm == "sweep":
        order = sorted(customers, key=lambda n: math.atan2(n.y - instance.depot.y, n.x - instance.depot.x))
        return split_by_capacity(order, params)
    if algorithm == "nearest":
        return nearest_routes(instance, customers, params)
    if algorithm == "grasp":
        best_routes: list[list[Node]] | None = None
        best_objective = float("inf")
        for _ in range(restarts):
            candidate = randomized_nearest_routes(instance, customers, params, rng)
            candidate = improve_routes(instance, candidate, stations, params)
            score = evaluate(instance, candidate, stations, params)["objective"]
            if score < best_objective:
                best_objective = score
                best_routes = candidate
        assert best_routes is not None
        return best_routes
    if algorithm in {"mp_eavns", "mp_eavns_nowarm", "mp_eavns_noshake", "mp_eavns_norepair"}:
        if algorithm == "mp_eavns_nowarm":
            seeds = [nearest_routes(instance, customers, params)]
        else:
            seeds = [
                warm_start_routes(instance, warm_start, customers, stations, params),
                split_by_capacity(sorted(customers, key=lambda n: (n.due, n.ready, n.node_id)), params),
                split_by_capacity(
                    sorted(customers, key=lambda n: math.atan2(n.y - instance.depot.y, n.x - instance.depot.x)),
                    params,
                ),
                nearest_routes(instance, customers, params),
            ]
            for _ in range(max(1, restarts)):
                seeds.append(randomized_nearest_routes(instance, customers, params, rng))
        best_seed = min(seeds, key=lambda routes: evaluate(instance, routes, stations, params)["objective"])
        no_shake = algorithm == "mp_eavns_noshake"
        no_repair = algorithm == "mp_eavns_norepair"
        return energy_aware_vns(
            instance, best_seed, stations, params, rng, vns_iterations,
            allow_shake=not no_shake,
            allow_repair=not no_repair,
        )
    if algorithm == "alns":
        return alns_routes(instance, customers, stations, params, rng, max(40, vns_iterations))
    raise ValueError(f"unknown algorithm: {algorithm}")


def insert_recharge(
    current: Node,
    target: Node,
    battery: float,
    stations: list[Node],
    params: DroneParams,
) -> tuple[Node | None, float]:
    reachable = [
        s
        for s in stations
        if distance(current, s) <= battery + 1e-9 and distance(s, target) <= params.range_limit + 1e-9
    ]
    if not reachable:
        return None, battery
    station = min(reachable, key=lambda s: distance(current, s) + distance(s, target))
    return station, params.range_limit


def evaluate(instance: Instance, routes: list[list[Node]], stations: list[Node], params: DroneParams) -> dict[str, float]:
    total_distance = 0.0
    total_tardiness = 0.0
    recharge_visits = 0
    infeasible = 0

    for route in routes:
        current = instance.depot
        time = 0.0
        battery = params.range_limit

        for customer in route + [instance.depot]:
            leg = distance(current, customer)
            if leg > battery + 1e-9:
                station, battery_after = insert_recharge(current, customer, battery, stations, params)
                if station is None:
                    infeasible += 1
                    total_distance += leg
                    time += leg / params.speed
                    battery = max(0.0, battery - leg)
                    current = customer
                    continue
                detour = distance(current, station)
                total_distance += detour
                time += detour / params.speed
                battery -= detour
                recharge_visits += 1
                recharge_amount = params.range_limit - battery
                time += params.recharge_fixed_time + params.recharge_time_per_unit * recharge_amount
                battery = battery_after
                current = station
                leg = distance(current, customer)

            total_distance += leg
            time += leg / params.speed
            battery -= leg
            if customer.kind == "c":
                if time < customer.ready:
                    time = customer.ready
                total_tardiness += max(0.0, time - customer.due)
                time += params.service_time
            current = customer

    objective = (
        total_distance
        + params.tardiness_weight * total_tardiness
        + params.drone_weight * len(routes)
        + params.infeasible_penalty * infeasible
    )
    return {
        "objective": objective,
        "distance": total_distance,
        "tardiness": total_tardiness,
        "routes": float(len(routes)),
        "recharges": float(recharge_visits),
        "infeasible_legs": float(infeasible),
    }


def improve_routes(
    instance: Instance, routes: list[list[Node]], stations: list[Node], params: DroneParams
) -> list[list[Node]]:
    improved = [list(route) for route in routes]
    best_score = evaluate(instance, improved, stations, params)["objective"]
    changed = True
    while changed:
        changed = False
        for ridx, route in enumerate(improved):
            if len(route) < 4:
                continue
            for i in range(len(route) - 2):
                for j in range(i + 2, len(route)):
                    candidate = [list(r) for r in improved]
                    candidate[ridx] = route[:i] + list(reversed(route[i:j])) + route[j:]
                    score = evaluate(instance, candidate, stations, params)["objective"]
                    if score + 1e-9 < best_score:
                        improved = candidate
                        best_score = score
                        changed = True
                        break
                if changed:
                    break
            if changed:
                break
    return improved


def best_two_opt(
    instance: Instance, routes: list[list[Node]], stations: list[Node], params: DroneParams, best_score: float
) -> tuple[list[list[Node]], float, bool]:
    for ridx, route in enumerate(routes):
        if len(route) < 4:
            continue
        for i in range(len(route) - 2):
            for j in range(i + 2, len(route) + 1):
                candidate = [list(r) for r in routes]
                candidate[ridx] = route[:i] + list(reversed(route[i:j])) + route[j:]
                score = evaluate(instance, candidate, stations, params)["objective"]
                if score + 1e-9 < best_score:
                    return clean_routes(candidate), score, True
    return routes, best_score, False


def best_relocate(
    instance: Instance, routes: list[list[Node]], stations: list[Node], params: DroneParams, best_score: float
) -> tuple[list[list[Node]], float, bool]:
    for src_idx, src_route in enumerate(routes):
        for src_pos, customer in enumerate(src_route):
            for dst_idx, dst_route in enumerate(routes):
                if src_idx != dst_idx and route_load(dst_route) + customer.demand > params.capacity:
                    continue
                for dst_pos in range(len(dst_route) + 1):
                    if src_idx == dst_idx and (dst_pos == src_pos or dst_pos == src_pos + 1):
                        continue
                    candidate = [list(r) for r in routes]
                    moved = candidate[src_idx].pop(src_pos)
                    insert_pos = dst_pos
                    if src_idx == dst_idx and dst_pos > src_pos:
                        insert_pos -= 1
                    candidate[dst_idx].insert(insert_pos, moved)
                    candidate = clean_routes(candidate)
                    score = evaluate(instance, candidate, stations, params)["objective"]
                    if score + 1e-9 < best_score:
                        return candidate, score, True
    return routes, best_score, False


def best_swap(
    instance: Instance, routes: list[list[Node]], stations: list[Node], params: DroneParams, best_score: float
) -> tuple[list[list[Node]], float, bool]:
    for first_idx, first_route in enumerate(routes):
        for first_pos, first_customer in enumerate(first_route):
            for second_idx in range(first_idx, len(routes)):
                second_route = routes[second_idx]
                start_pos = first_pos + 1 if first_idx == second_idx else 0
                for second_pos in range(start_pos, len(second_route)):
                    second_customer = second_route[second_pos]
                    if first_idx != second_idx:
                        first_load = route_load(first_route) - first_customer.demand + second_customer.demand
                        second_load = route_load(second_route) - second_customer.demand + first_customer.demand
                        if first_load > params.capacity or second_load > params.capacity:
                            continue
                    candidate = [list(r) for r in routes]
                    candidate[first_idx][first_pos], candidate[second_idx][second_pos] = (
                        candidate[second_idx][second_pos],
                        candidate[first_idx][first_pos],
                    )
                    score = evaluate(instance, candidate, stations, params)["objective"]
                    if score + 1e-9 < best_score:
                        return clean_routes(candidate), score, True
    return routes, best_score, False


def best_split(
    instance: Instance, routes: list[list[Node]], stations: list[Node], params: DroneParams, best_score: float
) -> tuple[list[list[Node]], float, bool]:
    for ridx, route in enumerate(routes):
        if len(route) < 2:
            continue
        for cut in range(1, len(route)):
            candidate = [list(r) for r in routes]
            left = route[:cut]
            right = route[cut:]
            candidate[ridx : ridx + 1] = [left, right]
            score = evaluate(instance, candidate, stations, params)["objective"]
            if score + 1e-9 < best_score:
                return clean_routes(candidate), score, True
    return routes, best_score, False


def best_merge(
    instance: Instance, routes: list[list[Node]], stations: list[Node], params: DroneParams, best_score: float
) -> tuple[list[list[Node]], float, bool]:
    for first_idx, first_route in enumerate(routes):
        for second_idx, second_route in enumerate(routes):
            if first_idx == second_idx:
                continue
            if route_load(first_route) + route_load(second_route) > params.capacity:
                continue
            for merged in (first_route + second_route, second_route + first_route):
                candidate = [list(r) for idx, r in enumerate(routes) if idx not in {first_idx, second_idx}]
                candidate.append(list(merged))
                score = evaluate(instance, candidate, stations, params)["objective"]
                if score + 1e-9 < best_score:
                    return clean_routes(candidate), score, True
    return routes, best_score, False


def shake(routes: list[list[Node]], params: DroneParams, rng: random.Random) -> list[list[Node]]:
    candidate = clean_routes(routes)
    if not candidate:
        return candidate
    if rng.random() < 0.5 and sum(len(route) for route in candidate) > 1:
        non_empty = [idx for idx, route in enumerate(candidate) if route]
        src_idx = rng.choice(non_empty)
        src_pos = rng.randrange(len(candidate[src_idx]))
        customer = candidate[src_idx].pop(src_pos)
        feasible_dst = [
            idx for idx, route in enumerate(candidate) if idx == src_idx or route_load(route) + customer.demand <= params.capacity
        ]
        dst_idx = rng.choice(feasible_dst)
        dst_pos = rng.randrange(len(candidate[dst_idx]) + 1)
        candidate[dst_idx].insert(dst_pos, customer)
    else:
        shuffle_candidates = [route for route in candidate if len(route) >= 2]
        if not shuffle_candidates:
            return candidate
        route = rng.choice(shuffle_candidates)
        rng.shuffle(route)
    return clean_routes(candidate)


def energy_aware_vns(
    instance: Instance,
    initial_routes: list[list[Node]],
    stations: list[Node],
    params: DroneParams,
    rng: random.Random,
    iterations: int,
    allow_shake: bool = True,
    allow_repair: bool = True,
) -> list[list[Node]]:
    current = clean_routes(initial_routes)
    if allow_repair:
        current = improve_routes(instance, current, stations, params)
    current_score = evaluate(instance, current, stations, params)["objective"]
    best = [list(route) for route in current]
    best_score = current_score
    neighborhoods = [best_two_opt, best_relocate, best_swap, best_split, best_merge]

    idle_rounds = 0
    for _ in range(max(1, iterations)):
        improved = False
        for neighborhood in neighborhoods:
            current, current_score, changed = neighborhood(instance, current, stations, params, current_score)
            if changed:
                improved = True
                idle_rounds = 0
                if current_score + 1e-9 < best_score:
                    best = [list(route) for route in current]
                    best_score = current_score
                break

        if not improved:
            if not allow_shake:
                break
            idle_rounds += 1
            shaken = shake(best, params, rng)
            if allow_repair:
                shaken = improve_routes(instance, shaken, stations, params)
            shaken_score = evaluate(instance, shaken, stations, params)["objective"]
            if shaken_score + 1e-9 < current_score or idle_rounds >= 4:
                current = shaken
                current_score = shaken_score
                idle_rounds = 0
                if current_score + 1e-9 < best_score:
                    best = [list(route) for route in current]
                    best_score = current_score

    return best


def alns_routes(
    instance: Instance,
    customers: list[Node],
    stations: list[Node],
    params: DroneParams,
    rng: random.Random,
    iterations: int,
) -> list[list[Node]]:
    """Adaptive Large Neighborhood Search with three destroy and two repair operators.

    Destroy operators: random removal, worst removal (highest cost contribution), related removal.
    Repair operators: greedy insertion (best position), regret-2 insertion.
    Operator weights are updated with a simple reward-based rule (sigma-scheme).
    Accept-or-reject by simulated-annealing-style criterion with cooling temperature.
    """
    if not customers:
        return []

    # Initial solution: best of nearest + EDD + sweep + improve.
    seeds = [
        nearest_routes(instance, customers, params),
        split_by_capacity(sorted(customers, key=lambda n: (n.due, n.ready, n.node_id)), params),
        split_by_capacity(
            sorted(customers, key=lambda n: math.atan2(n.y - instance.depot.y, n.x - instance.depot.x)),
            params,
        ),
    ]
    seeds = [improve_routes(instance, s, stations, params) for s in seeds]
    current = min(seeds, key=lambda r: evaluate(instance, r, stations, params)["objective"])
    current_score = evaluate(instance, current, stations, params)["objective"]
    best = [list(route) for route in current]
    best_score = current_score

    # Simulated-annealing acceptance.
    temperature = max(current_score * 0.05, 1.0)
    cooling = 0.995

    # Operator scoring.
    destroy_ops = ["random", "worst", "related"]
    repair_ops = ["greedy", "regret"]
    d_weight = {op: 1.0 for op in destroy_ops}
    r_weight = {op: 1.0 for op in repair_ops}
    d_score = {op: 0.0 for op in destroy_ops}
    r_score = {op: 0.0 for op in repair_ops}
    d_use = {op: 0 for op in destroy_ops}
    r_use = {op: 0 for op in repair_ops}

    def pick(weights: dict[str, float]) -> str:
        total = sum(weights.values())
        r = rng.uniform(0, total)
        cum = 0.0
        for k, w in weights.items():
            cum += w
            if r <= cum:
                return k
        return next(iter(weights))

    def flatten(routes: list[list[Node]]) -> list[Node]:
        out: list[Node] = []
        for route in routes:
            out.extend(route)
        return out

    def cost_contribution(routes: list[list[Node]], node: Node) -> float:
        # rough proxy: distance from neighbors in current route
        for route in routes:
            if node in route:
                idx = route.index(node)
                prev = route[idx - 1] if idx > 0 else instance.depot
                nxt = route[idx + 1] if idx + 1 < len(route) else instance.depot
                return distance(prev, node) + distance(node, nxt)
        return 0.0

    for it in range(max(1, iterations)):
        all_nodes = flatten(current)
        if not all_nodes:
            break
        # Choose how many to remove (10–30% of nodes).
        k = max(1, min(len(all_nodes), rng.randint(max(1, len(all_nodes) // 10), max(1, len(all_nodes) // 3))))

        # ---------- Destroy ----------
        d_op = pick(d_weight)
        d_use[d_op] += 1
        removed: list[Node] = []
        if d_op == "random":
            removed = rng.sample(all_nodes, k)
        elif d_op == "worst":
            scored = sorted(all_nodes, key=lambda n: -cost_contribution(current, n))
            removed = scored[:k]
        elif d_op == "related":
            seed = rng.choice(all_nodes)
            ordered = sorted(all_nodes, key=lambda n: distance(n, seed))
            removed = ordered[:k]
        removed_set = set(id(n) for n in removed)

        partial: list[list[Node]] = [[n for n in route if id(n) not in removed_set] for route in current]
        partial = clean_routes(partial)

        # ---------- Repair ----------
        r_op = pick(r_weight)
        r_use[r_op] += 1
        to_insert = list(removed)
        rng.shuffle(to_insert)

        def best_insertion(routes: list[list[Node]], node: Node) -> tuple[float, int, int]:
            # returns (delta_obj, route_idx, position). Adds a new route if all full.
            best_delta = float("inf")
            best_idx = -1
            best_pos = -1
            base_score = evaluate(instance, routes, stations, params)["objective"]
            for ridx, route in enumerate(routes):
                if route_load(route) + node.demand > params.capacity + 1e-9:
                    continue
                for pos in range(len(route) + 1):
                    cand = [list(r) for r in routes]
                    cand[ridx] = route[:pos] + [node] + route[pos:]
                    score = evaluate(instance, cand, stations, params)["objective"]
                    delta = score - base_score
                    if delta < best_delta:
                        best_delta = delta
                        best_idx = ridx
                        best_pos = pos
            # option: open a new route
            cand = [list(r) for r in routes] + [[node]]
            score = evaluate(instance, cand, stations, params)["objective"]
            delta = score - base_score
            if delta < best_delta:
                best_delta = delta
                best_idx = len(routes)
                best_pos = 0
            return best_delta, best_idx, best_pos

        if r_op == "greedy":
            for node in to_insert:
                delta, ridx, pos = best_insertion(partial, node)
                if ridx == len(partial):
                    partial.append([node])
                else:
                    partial[ridx] = partial[ridx][:pos] + [node] + partial[ridx][pos:]
        else:  # regret-2
            while to_insert:
                best_node = None
                best_regret = -float("inf")
                best_choice: tuple[float, int, int] = (float("inf"), -1, -1)
                for node in to_insert:
                    delta, ridx, pos = best_insertion(partial, node)
                    # second-best by removing the best route and recomputing
                    second_best = float("inf")
                    base_score = evaluate(instance, partial, stations, params)["objective"]
                    for ridx2, route2 in enumerate(partial):
                        if ridx2 == ridx:
                            continue
                        if route_load(route2) + node.demand > params.capacity + 1e-9:
                            continue
                        for pos2 in range(len(route2) + 1):
                            cand = [list(r) for r in partial]
                            cand[ridx2] = route2[:pos2] + [node] + route2[pos2:]
                            sc = evaluate(instance, cand, stations, params)["objective"] - base_score
                            if sc < second_best:
                                second_best = sc
                    regret = (second_best if second_best != float("inf") else delta + 1e6) - delta
                    if regret > best_regret:
                        best_regret = regret
                        best_node = node
                        best_choice = (delta, ridx, pos)
                if best_node is None:
                    break
                to_insert.remove(best_node)
                _, ridx, pos = best_choice
                if ridx == len(partial):
                    partial.append([best_node])
                else:
                    partial[ridx] = partial[ridx][:pos] + [best_node] + partial[ridx][pos:]

        partial = clean_routes(partial)
        cand_score = evaluate(instance, partial, stations, params)["objective"]

        # ---------- Accept ----------
        accepted = False
        reward = 0.0
        if cand_score + 1e-9 < best_score:
            best = [list(r) for r in partial]
            best_score = cand_score
            current = partial
            current_score = cand_score
            accepted = True
            reward = 3.0  # sigma_1: new global best
        elif cand_score + 1e-9 < current_score:
            current = partial
            current_score = cand_score
            accepted = True
            reward = 2.0  # sigma_2: better than current
        else:
            delta = cand_score - current_score
            if rng.random() < math.exp(-delta / max(temperature, 1e-9)):
                current = partial
                current_score = cand_score
                accepted = True
                reward = 1.0  # sigma_3: accepted worse

        if accepted:
            d_score[d_op] += reward
            r_score[r_op] += reward

        temperature *= cooling

        # Periodically update weights with reaction factor 0.3.
        if (it + 1) % 20 == 0:
            for op in destroy_ops:
                if d_use[op] > 0:
                    d_weight[op] = 0.7 * d_weight[op] + 0.3 * (d_score[op] / d_use[op])
                    d_score[op] = 0.0
                    d_use[op] = 0
                d_weight[op] = max(d_weight[op], 0.1)
            for op in repair_ops:
                if r_use[op] > 0:
                    r_weight[op] = 0.7 * r_weight[op] + 0.3 * (r_score[op] / r_use[op])
                    r_score[op] = 0.0
                    r_use[op] = 0
                r_weight[op] = max(r_weight[op], 0.1)

    return best


def run_experiment(args: argparse.Namespace) -> None:
    instance_dir = Path(args.instance_dir)
    result_dir = Path(args.results_dir)
    result_dir.mkdir(parents=True, exist_ok=True)

    if args.instances:
        instance_paths = [instance_dir / name for name in args.instances]
    else:
        small_pat = re.compile(r"^[cr]+[0-9]+C(5|10|15)\.txt$", re.IGNORECASE)
        large_pat = re.compile(r"^[cr]+[0-9]+_21\.txt$", re.IGNORECASE)
        if args.size == "small":
            pat = small_pat
        elif args.size == "large":
            pat = large_pat
        else:  # all
            pat = re.compile(f"{small_pat.pattern}|{large_pat.pattern}", re.IGNORECASE)
        instance_paths = [p for p in sorted(instance_dir.glob("*.txt")) if pat.match(p.name)][: args.limit]

    params = DroneParams(
        capacity=args.capacity,
        range_limit=args.range_limit,
        service_time=args.service_time,
    )
    rows: list[dict[str, str | float | int]] = []
    rng = random.Random(args.seed)
    route_history: dict[tuple[str, str, str], list[list[Node]]] = {}

    for path in instance_paths:
        instance = parse_instance(path)
        for period in range(1, args.periods + 1):
            customers = active_customers(instance, period, args.periods, args.scenario)
            for station_policy in args.station_policies:
                stations = select_stations(instance, customers, period, args.periods, station_policy)
                for algorithm in args.algorithms:
                    history_key = (instance.name, station_policy, algorithm)
                    started_at = time.perf_counter()
                    routes = build_routes(
                        algorithm,
                        instance,
                        customers,
                        stations,
                        params,
                        rng,
                        args.grasp_restarts,
                        args.vns_iterations,
                        route_history.get(history_key),
                    )
                    route_history[history_key] = [list(route) for route in routes]
                    runtime_seconds = time.perf_counter() - started_at
                    metrics = evaluate(instance, routes, stations, params)
                    rows.append(
                        {
                            "instance": instance.name,
                            "period": period,
                            "customers": len(customers),
                            "station_policy": station_policy,
                            "active_stations": len(stations),
                            "algorithm": algorithm,
                            "runtime_seconds": runtime_seconds,
                            **metrics,
                        }
                    )

    write_csv(result_dir / "results.csv", rows)
    write_summary(result_dir / "summary.csv", rows, ["algorithm"])
    write_summary(result_dir / "station_policy_summary.csv", rows, ["station_policy"])
    write_summary(result_dir / "algorithm_station_summary.csv", rows, ["algorithm", "station_policy"])


def write_csv(path: Path, rows: list[dict[str, str | float | int]]) -> None:
    if not rows:
        return
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def write_summary(path: Path, rows: list[dict[str, str | float | int]], group_keys: list[str]) -> None:
    groups: dict[tuple[str, ...], list[dict[str, str | float | int]]] = {}
    for row in rows:
        key = tuple(str(row[k]) for k in group_keys)
        groups.setdefault(key, []).append(row)

    summary_rows: list[dict[str, str | float | int]] = []
    for key, group in sorted(groups.items()):
        summary = {group_keys[idx]: value for idx, value in enumerate(key)}
        summary.update(
            {
                "runs": len(group),
                "objective_mean": mean(float(r["objective"]) for r in group),
                "distance_mean": mean(float(r["distance"]) for r in group),
                "tardiness_mean": mean(float(r["tardiness"]) for r in group),
                "routes_mean": mean(float(r["routes"]) for r in group),
                "recharges_mean": mean(float(r["recharges"]) for r in group),
                "infeasible_legs_mean": mean(float(r["infeasible_legs"]) for r in group),
                "runtime_seconds_mean": mean(float(r.get("runtime_seconds", 0.0)) for r in group),
            }
        )
        summary_rows.append(summary)
    write_csv(path, summary_rows)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Drone routing with recharging baselines over E-VRPTW instances.")
    parser.add_argument("--instance-dir", default=str(DEFAULT_INSTANCE_DIR))
    parser.add_argument("--results-dir", default=str(DEFAULT_RESULTS_DIR))
    parser.add_argument("--instances", nargs="*", default=[])
    parser.add_argument("--limit", type=int, default=200)
    parser.add_argument("--size", choices=["small", "large", "all"], default="small")
    parser.add_argument("--periods", type=int, default=4)
    parser.add_argument("--scenario", choices=["linear", "temporal", "spatial"], default="spatial")
    parser.add_argument(
        "--algorithms",
        nargs="+",
        default=["edd", "sweep", "nearest", "grasp", "alns", "mp_eavns", "mp_eavns_nowarm", "mp_eavns_noshake", "mp_eavns_norepair"],
    )
    parser.add_argument("--station-policies", nargs="+", default=["depot", "phased", "all"])
    parser.add_argument("--capacity", type=float, default=50.0)
    parser.add_argument("--range-limit", type=float, default=80.0)
    parser.add_argument("--service-time", type=float, default=5.0)
    parser.add_argument("--grasp-restarts", type=int, default=20)
    parser.add_argument("--vns-iterations", type=int, default=80)
    parser.add_argument("--seed", type=int, default=7)
    return parser.parse_args()


if __name__ == "__main__":
    run_experiment(parse_args())
