from flask import Flask, render_template_string, request
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import datetime
import io
import base64

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    name = ""
    img_individual = None
    img_mother = None
    img_father = None
    img_growing_up = None
    img_children = []
    children = []

    if request.method == 'POST':
        name = request.form['name']
        age = int(request.form['age'])
        sex = request.form['sex']
        mother_alive = request.form.get('mother_alive')
        mother_age = int(request.form['mother_age']) if mother_alive == 'yes' else None
        father_alive = request.form.get('father_alive')
        father_age = int(request.form['father_age']) if father_alive == 'yes' else None
        has_children = request.form.get('has_children')
        if has_children == 'yes':
            child_ages = request.form.getlist('child_age')
            child_sexes = request.form.getlist('child_sex')
            children = [(int(age), sex) for age, sex in zip(child_ages, child_sexes)]

        # Plotting based on the captured data
        life_expectancy = 80  # Assuming a life expectancy value for example

        # Generate individual plot
        if sex == 'M':
            life_expectancy = 79
            img_individual = plot_to_base64(individual, name, age, sex, life_expectancy)
        else:
            life_expectancy = 81
            img_individual = plot_to_base64(individual, name, age, sex, life_expectancy)

        # Generate parent plots
        if mother_alive == 'yes':
            img_mother = plot_to_base64(parent, "Mother", mother_age, 'F', life_expectancy)
        if father_alive == 'yes':
            img_father = plot_to_base64(parent, "Father", father_age, 'M', life_expectancy)

        # Generate growing up plot
        img_growing_up = plot_to_base64(growing_up, age)

        # Generate children plots
        for child_age, child_sex in children:
            img_child = plot_to_base64(child, child_age, child_sex)
            img_children.append(img_child)

    return render_template_string(html_template, name=name, img_individual=img_individual, img_mother=img_mother, img_father=img_father, img_growing_up=img_growing_up, img_children=img_children)

def plot_to_base64(func, *args):
    img = io.BytesIO()
    func(*args)
    plt.savefig(img, format='png')
    plt.close()
    img.seek(0)
    return base64.b64encode(img.getvalue()).decode()

html_template = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Your Life</title>
    <script>
        let childCount = 0;
        
        function toggleMotherAge(value) {
            document.getElementById('mother_age_div').style.display = value === 'yes' ? 'block' : 'none';
        }
        
        function toggleFatherAge(value) {
            document.getElementById('father_age_div').style.display = value === 'yes' ? 'block' : 'none';
        }
        
        function toggleChildren(value) {
            document.getElementById('children_div').style.display = value === 'yes' ? 'block' : 'none';
        }
        
        function addChild() {
            childCount++;
            const childDiv = document.createElement('div');
            childDiv.id = 'child_div_' + childCount;
            childDiv.innerHTML = `
                <label for="child_age_${childCount}">Child ${childCount} Age:</label>
                <input type="number" id="child_age_${childCount}" name="child_age"><br><br>
                <label for="child_sex_${childCount}">Child ${childCount} Sex:</label>
                <select id="child_sex_${childCount}" name="child_sex">
                    <option value="M">Male</option>
                    <option value="F">Female</option>
                </select><br><br>
            `;
            document.getElementById('add_child_button').insertAdjacentElement('beforebegin', childDiv);
        }
    </script>
</head>
<body>
    <h1>Your life</h1>
    <form method="post">
        <label for="name">Name:</label>
        <input type="text" id="name" name="name" required><br><br>

        <label for="age">Age:</label>
        <input type="number" id="age" name="age" required><br><br>
        
        <label for="sex">Sex:</label>
        <select id="sex" name="sex">
            <option value="M">Male</option>
            <option value="F">Female</option>
        </select><br><br>
        
        <label for="mother_alive">Is your mother alive?</label>
        <select id="mother_alive" name="mother_alive" onchange="toggleMotherAge(this.value)">
            <option value="no">No</option>
            <option value="yes">Yes</option>
        </select><br><br>
        
        <div id="mother_age_div" style="display:none;">
            <label for="mother_age">Mother's Age:</label>
            <input type="number" id="mother_age" name="mother_age"><br><br>
        </div>
        
        <label for="father_alive">Is your father alive?</label>
        <select id="father_alive" name="father_alive" onchange="toggleFatherAge(this.value)">
            <option value="no">No</option>
            <option value="yes">Yes</option>
        </select><br><br>
        
        <div id="father_age_div" style="display:none;">
            <label for="father_age">Father's Age:</label>
            <input type="number" id="father_age" name="father_age"><br><br>
        </div>
        
        <label for="has_children">Do you have children?</label>
        <select id="has_children" name="has_children" onchange="toggleChildren(this.value)">
            <option value="no">No</option>
            <option value="yes">Yes</option>
        </select><br><br>
        
        <div id="children_div" style="display:none;">
            <div id="children_entries"></div>
            <button type="button" id="add_child_button" onclick="addChild()">Add Child</button><br><br>
        </div>
        
        <input type="submit" value="Submit">
    </form>

    {% if img_individual %}
    <h2>You</h2>
    <img src="data:image/png;base64,{{ img_individual }}" alt="{{ name }}'s Plot"><br>
    {% endif %}

    {% if img_mother %}
    <h2>Your mother</h2>
    <img src="data:image/png;base64,{{ img_mother }}" alt="Mother's Plot"><br>
    {% endif %}

    {% if img_father %}
    <h2>Your father</h2>
    <img src="data:image/png;base64,{{ img_father }}" alt="Father's Plot"><br>
    {% endif %}

    {% if img_mother or img_father %}
        {% if img_growing_up %}
        <h2>Growing up</h2>
        <img src="data:image/png;base64,{{ img_growing_up }}" alt="Growing Up Plot"><br>
        {% endif %}
    {% endif %}
    
    {% for img_child in img_children %}
    <h2>Your child</h2>
    <img src="data:image/png;base64,{{ img_child }}" alt="Child Plot"><br>
    {% endfor %}
</body>
</html>
'''

def individual(name, age, sex, life_expectancy):
    grid_data = np.zeros((10, 10))
    grid_data.ravel()[:age] = 1
    grid_data.ravel()[age:life_expectancy] = 2

    palette = {0: "white", 1: "blue", 2: "gray"} if sex == 'M' else {0: "white", 1: "pink", 2: "gray"}
    grid_colors = sns.color_palette([palette[x] for x in np.unique(grid_data)])

    plt.figure(figsize=(7, 7))
    sns.heatmap(grid_data, cmap=grid_colors, linewidths=1, linecolor='black', cbar=False, square=True, xticklabels=False, yticklabels=False)
    #plt.title(f"{name}'s Plot")

def parent(name, age, sex, life_expectancy):
    grid_data = np.zeros((10, 10))
    grid_data.ravel()[:age] = 1
    grid_data.ravel()[age:life_expectancy] = 2

    palette = {0: "white", 1: "blue", 2: "lightblue"} if sex == 'M' else {0: "white", 1: "red", 2: "lightpink"}
    grid_colors = sns.color_palette([palette[x] for x in np.unique(grid_data)])

    plt.figure(figsize=(7, 7))
    sns.heatmap(grid_data, cmap=grid_colors, linewidths=1, linecolor='black', cbar=False, square=True, xticklabels=False, yticklabels=False)
    #plt.title(f"{name}'s Plot")

def growing_up(age, visit_parents_weeks=4):
    height = age + 1
    width = 52
    this_year = datetime.date.today().year
    yob = this_year - age - 1

    grid = np.zeros((height, width))
    grid[-19 - 1:] = 1

    mean = visit_parents_weeks
    std_dev = 1

    for i in range(0, age - 19):
        random_number = np.random.normal(mean, std_dev)
        rounded_integer = int(np.clip(np.round(random_number), 0, mean))
        grid[i, :rounded_integer] = 1

    cmap = sns.color_palette(["white", "grey"], as_cmap=True)

    plt.figure(figsize=(52/3, 45/3))
    ax = sns.heatmap(grid, cmap=cmap, cbar=False, linewidths=1, linecolor='black')
    ax.set_yticks(np.arange(height + 1))
    ax.set_yticklabels(reversed(range(yob, yob + height + 1)), rotation=0)
    ax.set_xticks([])

def child(age, sex, leave_home=18):
    grid_data = np.zeros((10, 10))
    grid_data.ravel()[:age] = 1
    grid_data.ravel()[age:leave_home] = 2

    palette = {0: "white", 1: "blue", 2: "lightblue"} if sex == 'M' else {0: "white", 1: "red", 2: "lightpink"}
    grid_colors = sns.color_palette([palette[x] for x in np.unique(grid_data)])

    plt.figure(figsize=(7, 7))
    sns.heatmap(grid_data, cmap=grid_colors, linewidths=1, linecolor='black', cbar=False, square=True, xticklabels=False, yticklabels=False)

if __name__ == '__main__':
    app.run(debug=True)
