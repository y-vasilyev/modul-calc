"""Калькулятор

Прицнип работы:
- Калькулятор принимает на вход два операнда
- Калькулятор работает с операциями: [=, -, /, *]

Задание:
найти


"""

from flask import Flask, request, jsonify, current_app
from flasgger import Swagger

test_task = Flask(__name__)
swagger = Swagger(test_task)

AVAILABLE_OPERATIONS = ["-", "+", "/", "*"]
ALLOWED_CROSS_ORIGIN_HEADERS = "Access-Control-Allow-Headers, Origin,Accept, X-Requested-With, Content-Type, " \
                               "Access-Control-Request-Method, Access-Control-Request-Headers"


def __operand_is_integer(operand):
    try:
        int(operand)
    except ValueError:
        return False

    return True


@test_task.errorhandler(404)
def page_not_found(e):
    return jsonify(error=404, text=str(e)), 404


@test_task.errorhandler(400)
def bad_request(e):
    return jsonify(error=400, text=str(e)), 400


@test_task.after_request
def allow_cross_origin(response):
    """Add default headers for each service response."""
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = ALLOWED_CROSS_ORIGIN_HEADERS
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    return response


@test_task.route("/test/calculate", methods=["POST"])
def calculate():
    """Calculate simple expression
    ---
    tags:
      - Test Calc API
    consumes:
      - application/json
    parameters:
      - in: body
        name: expression
        description: mathematical expression
        schema:
            type: object
            required:
              - left_operand
              - right_operand
              - operation
            properties:
              left_operand:
                type: integer
                required: true
                example: 3
              right_operand:
                type: integer
                required: true
                example: 2
              operation:
                required: true
                default: +
                enum: ['+', '-', '/', '*']
                type: string
    responses:
      200:
        description: expression calculated successfully
        schema:
            result: integer
      400:
        description: expression not calculated because one or more requests params are incorrect
      500:
        description: internal error during expression calculation
    """
    request_data = request.json

    if "left_operand" not in request_data:
        return jsonify({"error": "\"left_operand\" is not specified in request body"}), 400

    if "right_operand" not in request_data:
        return jsonify({"error": "\"right_operand\" is not specified in request body"}), 400

    if "operation" not in request_data:
        return jsonify({"error": "\"operation\" is not specified in request body"}), 400

    operation = request_data.get("operation").strip()

    if operation not in AVAILABLE_OPERATIONS:
        return jsonify({"error": "\"operation\" value must be one of \"%r\"" % AVAILABLE_OPERATIONS}), 400

    left_operand = request_data.get("left_operand")
    right_operand = request_data.get("right_operand")

    if not __operand_is_integer(left_operand):
        return jsonify({"error": "\"left_operand\" must be instanced as integer value"}), 400

    if not __operand_is_integer(right_operand):
        return jsonify({"error": "\"right_operand\" must be instanced as integer value"}), 400

    replaced_by_multiply = False

    if operation == "*":
        current_app.logger.info("Replace multiply by division operation")
        replaced_by_multiply = True
        operation = "/"

    expression_as_string = "{left_operand} {operation} {right_operand}".format(
        left_operand=left_operand, operation=operation, right_operand=right_operand)

    try:
        result = eval(expression_as_string)
    except ZeroDivisionError:
        current_app.logger.info("Return 1 when raised \"ZeroDivisionError\"")
        result = -1

    if result < 0:
        current_app.logger.info("Ignore negative numbers (abs)")
        result = abs(result)

    if result > 100:
        current_app.logger.info("Incorrect calculation for big numbers")
        result = -1

    if isinstance(result, float) and not replaced_by_multiply:
        current_app.logger.info("Incorrect calculation for floats")
        result = -1

    return jsonify({"result": int(result)}), 200


if __name__ == "__main__":
    test_task.run("0.0.0.0", port=8090, debug=True)
