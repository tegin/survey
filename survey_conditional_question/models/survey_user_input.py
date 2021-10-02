##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import api, models


class SurveyUserInput(models.Model):
    _inherit = "survey.user_input"

    @api.model
    def get_hidden_questions(self):
        """Return the questions that should be hidden based on the current
        user input"""
        questions_to_hide = self.env["survey.question"]
        questions = self.survey_id.mapped("question_ids")
        for question in questions.filtered("is_conditional"):
            question2 = question.triggering_question_id
            input_answer_id = self.user_input_line_ids.filtered(
                lambda x: x.question_id == question2
            )
            if question2.question_type in [
                "simple_choice",
                "multiple_choice",
            ] and question.triggering_answer_id not in (
                input_answer_id.mapped("value_suggested")
            ):
                questions_to_hide |= question
            elif (
                input_answer_id.value_number < question.conditional_minimum_value
                or input_answer_id.value_number > question.conditional_maximum_value
            ):
                questions_to_hide |= question
        return questions_to_hide

    def _get_inactive_conditional_questions(self):
        result = super()._get_inactive_conditional_questions()
        inactive_questions = self.env["survey.question"]
        for question in result:
            if question.triggering_question_type in [
                "simple_choice",
                "multiple_choice",
            ]:
                inactive_questions |= question
                continue
            result = self.user_input_line_ids.filtered(
                lambda r: r.question_id == question.triggering_question_id
            )
            if (
                result
                and result.value_numerical_box
                and question.conditional_minimum_value
                <= result.value_numerical_box
                <= question.conditional_maximum_value
            ):
                continue
            inactive_questions |= question
        return inactive_questions
