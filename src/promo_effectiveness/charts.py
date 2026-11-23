"""Dependency-light SVG charts for descriptive campaign analysis."""

import math
from pathlib import Path


def campaign_assignment_overlap_svg(data):
    """Create the existing assignment/co-assignment chart as vector SVG."""

    data = data.sort_values('campaign_id').reset_index(drop=True)
    width, height = 1500, 1030
    top, row_step = 160, 26
    left1, plot1 = 185, 510
    left2, plot2 = 905, 510
    max_assigned = max(1, int(data.assigned_households.max()))
    max_coassigned = max(1, int(data.households_also_assigned_any.max()))
    ybase = top + row_step * (len(data) - 1)
    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
           '<rect width="100%" height="100%" fill="#ffffff"/>',
           '<style>text{font-family:Arial,Helvetica,sans-serif;fill:#243447}.title{font-size:27px;font-weight:700}.sub{font-size:15px;fill:#526273}.head{font-size:17px;font-weight:700}.tick{font-size:12px;fill:#526273}.lab{font-size:12px}.count{font-size:11px;fill:#263849}</style>',
           '<text x="60" y="45" class="title">Campaign assignment and household co-assignment</text>',
           '<text x="60" y="73" class="sub">Assignment is targeting; scheduled overlap is not verified exposure or an assignment timestamp.</text>',
           f'<text x="{left1}" y="120" class="head">Unique assigned households</text>',
           f'<text x="{left2}" y="120" class="head">Assigned households also assigned elsewhere</text>',
           f'<text x="{left2}" y="140" class="sub">Blue: any other campaign; orange: other campaign dates overlap this schedule</text>']
    ticks1 = [round(max_assigned * i / 5) for i in range(6)]
    ticks2 = [round(max_coassigned * i / 5) for i in range(6)]
    for tick in sorted(set(ticks1)):
        x = left1 + plot1 * tick / max_assigned
        svg.append(f'<line x1="{x:.1f}" y1="{top-9}" x2="{x:.1f}" y2="{ybase+12}" stroke="#e3e8ee"/>')
        svg.append(f'<text x="{x:.1f}" y="{ybase+34}" text-anchor="middle" class="tick">{tick}</text>')
    for tick in sorted(set(ticks2)):
        x = left2 + plot2 * tick / max_coassigned
        svg.append(f'<line x1="{x:.1f}" y1="{top-9}" x2="{x:.1f}" y2="{ybase+12}" stroke="#e3e8ee"/>')
        svg.append(f'<text x="{x:.1f}" y="{ybase+34}" text-anchor="middle" class="tick">{tick}</text>')
    for i, row in data.iterrows():
        y = top + i * row_step
        assigned = int(row.assigned_households)
        any_count = int(row.households_also_assigned_any)
        overlap_count = int(row.households_also_assigned_schedule_overlap)
        svg.append(f'<text x="155" y="{y+4}" text-anchor="end" class="lab">C{int(row.campaign_id)}</text>')
        bar1 = plot1 * assigned / max_assigned
        svg.append(f'<rect x="{left1}" y="{y-8}" width="{bar1:.1f}" height="15" rx="2" fill="#9bb5ca"/>')
        svg.append(f'<text x="{left1+bar1+5:.1f}" y="{y+4}" class="count">{assigned:,}</text>')
        anyw = plot2 * any_count / max_coassigned
        overlapw = plot2 * overlap_count / max_coassigned
        svg.append(f'<rect x="{left2}" y="{y-8}" width="{anyw:.1f}" height="15" rx="2" fill="#4c78a8"/>')
        svg.append(f'<rect x="{left2}" y="{y-8}" width="{overlapw:.1f}" height="15" rx="2" fill="#e28e2c"/>')
        svg.append(f'<text x="{left2+anyw+5:.1f}" y="{y+4}" class="count">{any_count:,} / {overlap_count:,}</text>')
    svg.extend([
        f'<text x="{left1+plot1/2}" y="{height-45}" text-anchor="middle" class="lab">Assigned households</text>',
        f'<text x="{left2+plot2/2}" y="{height-45}" text-anchor="middle" class="lab">Co-assigned households (any / overlapping schedule)</text>',
        f'<rect x="{left2}" y="91" width="14" height="14" fill="#4c78a8"/><text x="{left2+21}" y="103" class="lab">Other campaign assignment</text>',
        f'<rect x="{left2+240}" y="91" width="14" height="14" fill="#e28e2c"/><text x="{left2+261}" y="103" class="lab">Date-overlapping schedule subset</text>',
        '<text x="60" y="1010" class="sub">Co-assignment counts are distinct households. Campaign-table records have no assignment-event timestamp; overlap is based on scheduled date ranges.</text>',
        '</svg>'
    ])
    return '\n'.join(svg)


def campaign26_spending_svg(household_periods, summary):
    """Create the existing P10-P90 household spending profile as vector SVG."""

    width, height = 1360, 830
    left, right, top, bottom = 120, 65, 112, 650
    plot_height = bottom - top
    periods = ['Pre', 'Campaign', 'Post']
    groups = ['Assigned to Campaign 26', 'Not assigned to Campaign 26']
    colors = {groups[0]: '#315a7d', groups[1]: '#df7b46'}
    quantiles = {}
    max_p90 = 0.0
    for group in groups:
        for period in periods:
            values = household_periods.loc[
                (household_periods.assignment_group == group)
                & (household_periods.period_label == period),
                'spend_per_28d_equivalent',
            ].astype(float)
            qs = [float(values.quantile(q)) for q in (.10, .25, .50, .75, .90)]
            quantiles[(group, period)] = qs
            max_p90 = max(max_p90, qs[-1])
    upper = max(50.0, max_p90 * 1.18)
    ymax = math.log1p(upper)

    def ycoord(value):
        return bottom - (math.log1p(max(0, float(value))) / ymax) * plot_height

    ticks = [0, 10, 25, 50, 100, 200, 500, 1000, 2500, 5000, 10000, 25000]
    centers = [300, 680, 1060]
    offsets = {groups[0]: -60, groups[1]: 60}
    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
           '<rect width="100%" height="100%" fill="#ffffff"/>',
           '<style>text{font-family:Arial,Helvetica,sans-serif;fill:#25364a}.title{font-size:25px;font-weight:700}.sub{font-size:14px;fill:#526273}.axis{font-size:13px;fill:#526273}.period{font-size:15px;font-weight:700}.small{font-size:11px;fill:#526273}.legend{font-size:13px}</style>',
           '<text x="60" y="43" class="title">Campaign 26: observed household spending profile</text>',
           '<text x="60" y="68" class="sub">Assigned vs not assigned to Campaign 26; group differences are descriptive, not campaign impact.</text>']
    for tick in ticks:
        if tick > upper:
            continue
        y = ycoord(tick)
        svg.append(f'<line x1="{left}" y1="{y:.1f}" x2="{width-right}" y2="{y:.1f}" stroke="#e3e8ee"/>')
        svg.append(f'<text x="{left-12}" y="{y+4:.1f}" text-anchor="end" class="axis">${tick:,}</text>')
    svg.append(f'<line x1="{left}" y1="{top}" x2="{left}" y2="{bottom}" stroke="#637487"/>')
    svg.append(f'<line x1="{left}" y1="{bottom}" x2="{width-right}" y2="{bottom}" stroke="#637487"/>')
    for period_index, period in enumerate(periods):
        center = centers[period_index]
        svg.append(f'<text x="{center}" y="{bottom+30}" text-anchor="middle" class="period">{period}</text>')
        for group in groups:
            x = center + offsets[group]
            p10, p25, p50, p75, p90 = quantiles[(group, period)]
            color = colors[group]
            y10, y25, y50, y75, y90 = [ycoord(v) for v in (p10, p25, p50, p75, p90)]
            svg.extend([
                f'<line x1="{x}" y1="{y90:.1f}" x2="{x}" y2="{y10:.1f}" stroke="{color}" stroke-width="2"/>',
                f'<line x1="{x-12}" y1="{y90:.1f}" x2="{x+12}" y2="{y90:.1f}" stroke="{color}" stroke-width="2"/>',
                f'<line x1="{x-12}" y1="{y10:.1f}" x2="{x+12}" y2="{y10:.1f}" stroke="{color}" stroke-width="2"/>',
                f'<rect x="{x-24}" y="{min(y75,y25):.1f}" width="48" height="{max(1,abs(y25-y75)):.1f}" fill="{color}" fill-opacity="0.28" stroke="{color}" stroke-width="2"/>',
                f'<line x1="{x-24}" y1="{y50:.1f}" x2="{x+24}" y2="{y50:.1f}" stroke="{color}" stroke-width="3"/>',
            ])
            row = summary.loc[
                (summary.assignment_group == group) & (summary.period == period)
            ].iloc[0]
            zero_pct = 100 * row.zero_purchase_households / row.households_including_zeros
            label = ('A' if group == groups[0] else 'N') + f': {zero_pct:.0f}% zero'
            svg.append(f'<text x="{x}" y="{bottom+49}" text-anchor="middle" class="small">{label}</text>')
    svg.extend([
        f'<text x="{(left+width-right)/2}" y="{bottom+80}" text-anchor="middle" class="axis">Scheduled period (campaign window values scaled to 28 days)</text>',
        f'<text x="{left}" y="{top-22}" class="small">$ per household per 28-day equivalent; log1p display scale</text>',
        f'<rect x="790" y="86" width="15" height="15" fill="{colors[groups[0]]}" fill-opacity="0.55"/><text x="812" y="99" class="legend">Assigned (n=332)</text>',
        f'<rect x="980" y="86" width="15" height="15" fill="{colors[groups[1]]}" fill-opacity="0.55"/><text x="1002" y="99" class="legend">Not assigned (n=2,168; observational)</text>',
        '<text x="60" y="785" class="small">Boxes: P25-P75; center line: median; whiskers: P10-P90. Zero-purchase households are included. Recorded sales only; not verified exposure.</text>',
        '</svg>'
    ])
    return '\n'.join(svg)


def save_svg(svg: str, output_path: Path) -> Path:
    """Write an SVG under the requested documentation path."""

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(svg, encoding='utf-8')
    return path
