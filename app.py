import flet as ft
import json
import db

def main(page:ft.Page):
    page.title = "Problem Set"
    page.window.width = 390
    page.window.height = 844

    statement_text = ft.Text(size=20)
    result_text = ft.Text(size=15)
    options_column = ft.Column()
    statement_image = ft.Image(src="", width = 600, fit = ft.BoxFit.CONTAIN)

    current_problem = None 

    def load_new_problem():
        nonlocal current_problem, statement_image
        current_problem = db.get_random_unsolved_problem()
        result_text.value = ""

        if current_problem is None:
            statement_text.value = "No unsolved problems left!"
            options_column.controls = []
            page.update()
            return

        statement_image.src = current_problem["statement_image"]
        options = json.loads(current_problem["options"])

        buttons = [statement_image]

        for opt in options:
            if opt["type"] == "text":
                button_content = ft.Row([
                    ft.Text(f"{opt['id']}:", color=ft.Colors.WHITE),
                    ft.Image(src=opt["image_path"], height=45, fit=ft.BoxFit.CONTAIN)
                ])
            else:
                button_content = ft.Row([
                    ft.Text(f"{opt['id']}:", color=ft.Colors.WHITE),
                    ft.Image(src=opt["value"], width=120, height=45, fit=ft.BoxFit.CONTAIN)
                ])
            buttons.append(
                ft.ElevatedButton(
                    content=button_content,
                    on_click = lambda e, opt_id=opt["id"]: check_answer(opt_id)
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
    # page.add(
    # ft.Image(src="images/q2_optA.png", width=200, height=80, fit=ft.BoxFit.CONTAIN),
    # statement_text, statement_image, options_column, result_text, next_button
    # )
    page.add(statement_text, options_column, result_text, next_button)

    load_new_problem()


ft.app(target=main)