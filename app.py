import flet as ft
import asyncio
import json
import db
from PIL import Image as PILImage

def main(page: ft.Page):
    page.title = "Problem Set"
    page.window.width = 390
    page.window.height = 844

    selected_problem = None

    def build_home_view():
        nonlocal selected_problem

        async def go_to_problem(e):
            await page.push_route("/problem")

        async def go_to_specific_problem(e, problem):
            nonlocal selected_problem
            selected_problem = problem
            await page.push_route("/problem")

        async def go_to_about(e):
            await page.push_route("/about")

        async def go_to_stats(e):
            await page.push_route("/stats")

        def build_rows(problems):
            return [
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(p["source"])),
                        ft.DataCell(ft.Text(str(p["difficulty"]))),
                        ft.DataCell(ft.Text("Yes" if p["solved"] else "No")),
                        ft.DataCell(ft.Text(str(p["attempts"])))
                    ],
                    on_select_change=lambda e, prob=p: page.run_task(go_to_specific_problem, e, prob)
                )
                for p in problems
            ]

        def refresh_table(e):
            source = None if source_dropdown.value == "all" else source_dropdown.value 
            difficulty = None if difficulty_dropdown.value == "all" else difficulty_dropdown.value
            solved = None if solved_dropdown.value == "all" else solved_dropdown.value
            problems = db.get_all_probs_with_progress(source, difficulty, solved)
            table.rows = build_rows(problems)
            page.update()

        initial_problems = db.get_all_probs_with_progress()

        source_dropdown = ft.Dropdown(
            label="Source",
            options=[
                ft.dropdown.Option(key="all", text="All"),
                ft.dropdown.Option(key="TMUA Paper 1", text="TMUA Paper 1"),
                ft.dropdown.Option(key="TMUA Paper 2", text="TMUA Paper 2"),
                ft.dropdown.Option(key="MAT", text="MAT"),
                ft.dropdown.Option(key="SMC", text="SMC"),
            ],
            value="all",
            on_select=refresh_table
        )

        difficulty_dropdown = ft.Dropdown(
            label="Difficulty",
            options=[
                ft.dropdown.Option(key="all", text="All"),
                ft.dropdown.Option(key="1", text="1"),
                ft.dropdown.Option(key="2", text="2"),
                ft.dropdown.Option(key="3", text="3")
            ],
            value="all",
            on_select=refresh_table
        )

        solved_dropdown = ft.Dropdown(
            label="Solved",
            options=[
                ft.dropdown.Option(key="all", text="All"),
                ft.dropdown.Option(key=1, text="Yes"),
                ft.dropdown.Option(key=0, text="No"),
            ],
            value="all",
            on_select=refresh_table
        )

        table = ft.DataTable(
            columns=[ft.DataColumn(ft.Text("Source")),
                     ft.DataColumn(ft.Text("Difficulty")),
                     ft.DataColumn(ft.Text("Solved")),
                     ft.DataColumn(ft.Text("Attempts")),
            ],
            rows=build_rows(initial_problems),
            column_spacing=20
        )

        table_column = ft.Column([table], scroll=ft.ScrollMode.AUTO, expand=True)

        return ft.View(
            route="/",
            controls=[
                ft.Container(content=ft.Text("Problem Set", size=24), alignment=ft.Alignment.CENTER),
                ft.ElevatedButton("About", on_click=go_to_about),
                ft.ElevatedButton("User stats", on_click=go_to_stats),
                ft.ElevatedButton("Try a random problem", on_click=go_to_problem),
                source_dropdown,
                difficulty_dropdown,
                solved_dropdown,
                table_column
                ],
            spacing=15
        )

    def build_problem_view(problem=None):
        if problem is None:
            problem = db.get_random_unsolved_problem()

        async def go_home(e):
            await page.push_route("/")

        if problem is None:
            return ft.View(
                route="/problem",
                controls=[
                    ft.Text("No unsolved problems left!"),
                    ft.ElevatedButton("Back home",on_click=go_home)
                ]
            )

        difficulty_text = ft.Text("Difficulty: ", size=15)
        empty_star = ft.Icon(ft.Icons.STAR_BORDER, color=ft.Colors.WHITE, size=20)
        star = ft.Icon(ft.Icons.STAR, color=ft.Colors.WHITE, size=20)
        result_text = ft.Text(size=15)
        main_column = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True, spacing=20, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
        home_button = ft.ElevatedButton("Exit",on_click=go_home)
        main_column_contents = [home_button]
        statement_image = ft.Image(src="", width = 300, fit = ft.BoxFit.CONTAIN)

        def check_answer(selected_option_id):
            is_correct = db.check_solution(problem["id"],selected_option_id)
            if is_correct:
                result_text.value = "Correct"
                result_text.color = ft.Colors.GREEN 
            else:
                result_text.value = "Wrong. Try again."
                result_text.color = ft.Colors.RED 

        def next_problem():
            page.views[-1] = build_problem_view()
            page.update()

        statement_image.src = problem["statement_image"]
        main_column_contents.append(statement_image)
        
        problem_difficulty = problem["difficulty"]
        difficulty_row_contents = [difficulty_text]
        for i in range(problem_difficulty):
            difficulty_row_contents.append(star)
        while len(difficulty_row_contents) < 4:
            difficulty_row_contents.append(empty_star)
        difficulty_row = ft.Row(difficulty_row_contents)
        main_column_contents.append(difficulty_row)

        options = json.loads(problem["options"])
        for opt in options:
            if opt["type"] == "text":
                button_content = ft.Row([
                    ft.Text(f"{opt['id']}:", color=ft.Colors.WHITE),
                    ft.Image(src=opt["image_path"], width=300, height=45, fit=ft.BoxFit.CONTAIN)
                ])
            else:
                button_content = ft.Row([
                    ft.Text(f"{opt['id']}:", color=ft.Colors.WHITE),
                    ft.Image(src=opt["value"], width=300, height=45, fit=ft.BoxFit.CONTAIN)
                ])
            main_column_contents.append(
                ft.ElevatedButton(
                    content=button_content,
                    on_click = lambda e, opt_id=opt["id"]: check_answer(opt_id)
                )
            )

        main_column_contents.append(result_text)

        next_button = ft.ElevatedButton("Next problem", on_click=next_problem)
        main_column_contents.append(next_button)

        main_column.controls = main_column_contents

        return ft.View(
            route="/problem",
            controls=[main_column]
        )

    def build_about_view():
        async def go_home(e):
            await page.push_route("/")

        return ft.View(
            route="/about",
            controls=[
                ft.Text("Welcome to Problem Set!\n\nThis is a small app built to help with preparation for the TMUA and other multiple choice mathematical admissions tests.\n\nA few notes:\n- Questions are ranked by difficulty on a scale of 1 (easiest) - 3 (hardest). Allow a level of subjectivity in these rankings.\n- The ampunt of XP awarded for the correct completion of a problem is equal to the difficulty of the problem.\n- Points are only awarded on the first attempt of a problem.\n- To start attempting problems, either select a specific problem from the table on the Home page or try a random problem.\n\nGood luck and, most importantly, enjoy your maths!\n"),
                ft.ElevatedButton("Home",on_click=go_home)
            ]
        )

    def build_stats_view():
        async def go_home(e):
            await page.push_route("/")

        total = db.get_total_problems()
        solved = db.get_total_solved()
        percent_solved = round((solved/total)*100) if total > 0 else 0
        first_attempt_correct = db.get_first_attempt_correct()
        percent_first_attempt_correct = round((first_attempt_correct/solved)*100) if solved > 0 else 0 
        xp = db.get_total_xp()

        return ft.View(
            route="/stats",
            controls=[
                ft.ElevatedButton("Exit", on_click=go_home),
                ft.Row(
                    [ft.Text("User stats", size=30)],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                ft.Text(f"Total problems solved: {solved}/{total} ({percent_solved}%)"),
                ft.Text(f"First attempt accuracy: {percent_first_attempt_correct}%"),
                ft.Text(f"Total XP: {xp}"),
            ]
        )

    def route_change(e):
        nonlocal selected_problem

        page.views.clear()
        page.views.append(build_home_view())
        if page.route == "/problem":
            page.views.append(build_problem_view(selected_problem))
            selected_problem = None
        if page.route == "/about":
            page.views.append(build_about_view())
        if page.route == "/stats":
            page.views.append(build_stats_view())
        page.update()


    page.on_route_change = route_change
    route_change(None)

ft.run(main)
