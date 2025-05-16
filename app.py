from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

def calculate_individual_totals(items, total_tax, total_tip, tax_split_method, tip_split_method):
    subtotals = {}
    items_per_person = {}

    for item in items:
        shared = item['shared']
        share_cost = item['cost'] / len(shared)
        for p in shared:
            subtotals.setdefault(p, 0.0)
            items_per_person.setdefault(p, [])
            subtotals[p] += share_cost
            items_per_person[p].append({'name': item['name'], 'cost': share_cost})

    grand_sub = sum(subtotals.values())
    people = list(subtotals.keys())
    n = len(people)

    per_tax = {}
    per_tip = {}
    for p in people:
        if tax_split_method == 'equal':
            per_tax[p] = total_tax / n
        else:
            per_tax[p] = (subtotals[p] / grand_sub) * total_tax if grand_sub else 0
        if tip_split_method == 'equal':
            per_tip[p] = total_tip / n
        else:
            per_tip[p] = (subtotals[p] / grand_sub) * total_tip if grand_sub else 0

    results = {}
    for p in people:
        total = subtotals[p] + per_tax[p] + per_tip[p]
        results[p] = {
            'subtotal': subtotals[p],
            'tax': per_tax[p],
            'tip': per_tip[p],
            'total': total,
            'purchased_items': items_per_person[p]
        }
    return results

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # collect people
        people = request.form.getlist('people[]')
        
        # collect items
        num_items_str = request.form.get('num_items', '0')
        try:
            num_items = int(num_items_str)
        except ValueError:
            num_items = 0 # Default to 0 if conversion fails

        items = []
        for i in range(num_items):
            name = request.form.get(f'item_name_{i}', '')
            cost_str = request.form.get(f'item_cost_{i}', '0.0')
            try:
                cost = float(cost_str)
            except ValueError:
                cost = 0.0 # Default to 0.0 if conversion fails
            
            shared_raw = request.form.get(f'item_shared_{i}', '').strip()
            if shared_raw.lower() == 'all':
                shared = people
            else:
                shared = [s.strip() for s in shared_raw.split(',') if s.strip() and s.strip() in people] # ensure s.strip() is not empty
            items.append({'name': name, 'cost': cost, 'shared': shared})

        total_tax_str = request.form.get('total_tax', '0.0')
        try:
            total_tax = float(total_tax_str)
        except ValueError:
            total_tax = 0.0

        total_tip_str = request.form.get('total_tip', '0.0')
        try:
            total_tip = float(total_tip_str)
        except ValueError:
            total_tip = 0.0
            
        tax_method = request.form.get('tax_method', 'proportional')
        tip_method = request.form.get('tip_method', 'proportional')
        
        results = calculate_individual_totals(items, total_tax, total_tip, tax_method, tip_method)
        return render_template('results.html', results=results)

    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)