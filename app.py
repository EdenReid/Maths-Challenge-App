import flet as ft
import json
import db

def main(page:ft.Page):
    page.title = "Problem Set"

    statement_text = ft.Text(size=20)
    result_text = ft.Text(size=15)
    options_column = ft.Column()

    current_problem = None 

    def load_new_problem():
        nonlocal current_problem
        current_problem = db.get_random_unsolved_problem()
        result_text.value = ""

        if current_problem is None:
            statement_text.value = "No unsolved problems left!"
            options_column.controls = []
            page.update()
            return

        statement_text.value = current_problem["statement"]
        options = json.loads(current_problem["options"])

        buttons = []

        for opt in options:
            label = opt["value"] if opt["type"] == "text" else f"[Image: {opt["value"]}]"
            buttons.append(
                ft.ElevatedButton(
                    f"{opt['id']}: {label}",
                    on_click=lambda e, opt_id=opt["id"]: check_answer(opt_id)
                )
            )
        options_column.controls = buttons
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

    page.add(statement_text, options_column, result_text, next_button)

    load_new_problem()


ft.app(target=main)