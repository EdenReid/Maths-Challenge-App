import flet as ft
import json
import db
from PIL import Image as PILImage


def main(page:ft.Page):
    page.title = "Problem Set"
    page.window.width = 390
    page.window.height = 844

    statement_text = ft.Text(size=20)
    difficulty_text = ft.Text("Difficulty: ", size=15)
    empty_star = ft.Icon(ft.Icons.STAR_BORDER, color=ft.Colors.WHITE, size=20)
    star = ft.Icon(ft.Icons.STAR, color=ft.Colors.WHITE, size=20)
    result_text = ft.Text(size=15)
    main_column = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True, spacing=20, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
    main_column_contents = []
    statement_image = ft.Image(src="", width = 300, fit = ft.BoxFit.CONTAIN)

    current_problem = None 

    def load_new_problem():
        nonlocal current_problem, statement_image
        current_problem = db.get_random_unsolved_problem()
        result_text.value = ""

        main_column_contents.clear()

        if current_problem is None:
            statement_text.value = "No unsolved problems left!"
            main_column_contents.append(statement_text)
            main_column.controls = main_column_contents
            page.update()
            return

        problem_difficulty = current_problem["difficulty"]
        difficulty_row_contents = [difficulty_text]
        for i in range(problem_difficulty):
            difficulty_row_contents.append(star)
        while len(difficulty_row_contents) < 4:
            difficulty_row_contents.append(empty_star)
        difficulty_row = ft.Row(difficulty_row_contents)
        
        statement_image.src = current_problem["statement_image"]
        options = json.loads(current_problem["options"])

        main_column_contents.append(statement_image)
        main_column_contents.append(difficulty_row)

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
        main_column_contents.append(next_button)

        main_column.controls = main_column_contents
        page.update()

    def check_answer(selected_option_id):
        is_correct = db.check_solution(current_problem["id"],selected_option_id)
        if is_correct:
            result_text.value = "Correct"
            result_text.color = ft.Colors.GREEN 
        else:
            result_text.value = "Wrong. Try again."
            result_text.color = ft.Colors.RED 

        page.update()
    
    next_button = ft.ElevatedButton("Next problem", on_click=lambda e: load_new_problem())

    load_new_problem()

    page.add(main_column)


ft.app(target=main)