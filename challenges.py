from flask import Blueprint, request, jsonify
import json
import subprocess
import tempfile
import os

challenges_bp = Blueprint('challenges', __name__)

class CodeChallenge:
    def __init__(self):
        self.challenges = self.load_challenges()
    
    def load_challenges(self):
        return {
            1: {
                'title': 'FizzBuzz',
                'description': 'Напишите функцию, которая возвращает "Fizz" для чисел кратных 3, "Buzz" для кратных 5, и "FizzBuzz" для кратных 15. Для остальных чисел возвращайте само число как строку.',
                'tests': [
                    {'input': 3, 'expected': 'Fizz'},
                    {'input': 5, 'expected': 'Buzz'},
                    {'input': 15, 'expected': 'FizzBuzz'},
                    {'input': 7, 'expected': '7'},
                    {'input': 30, 'expected': 'FizzBuzz'}
                ],
                'template': 'def fizzbuzz(n):\n    # Ваш код здесь\n    pass'
            },
            2: {
                'title': 'Палиндром',
                'description': 'Проверьте, является ли строка палиндромом (читается одинаково слева направо и справа налево). Игнорируйте регистр и пробелы.',
                'tests': [
                    {'input': 'радар', 'expected': True},
                    {'input': 'привет', 'expected': False},
                    {'input': 'А роза упала на лапу Азора', 'expected': True}
                ],
                'template': 'def is_palindrome(s):\n    # Ваш код здесь\n    pass'
            },
            3: {
                'title': 'Сумма чисел в строке',
                'description': 'Найдите сумму всех чисел в строке. Числа могут быть отрицательными и с плавающей точкой.',
                'tests': [
                    {'input': 'abc 123 def 45.6', 'expected': 168.6},
                    {'input': '1 -2 3.5 -4.2', 'expected': -1.7},
                    {'input': 'no numbers here', 'expected': 0}
                ],
                'template': 'def sum_numbers_in_string(s):\n    # Ваш код здесь\n    pass'
            }
        }
    
    def run_python_code(self, code, tests):
        results = []
        temp_file = None
        
        try:
            # Создаем временный файл
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(code)
                temp_file = f.name
            
            # Выполняем тесты
            for test in tests:
                try:
                    # Безопасное выполнение кода в изолированной среде
                    exec_globals = {}
                    exec(code, exec_globals)
                    
                    # Находим последнюю определенную функцию
                    func_name = None
                    for name in exec_globals:
                        if callable(exec_globals[name]) and not name.startswith('_'):
                            func_name = name
                            break
                    
                    if not func_name:
                        results.append({
                            'error': 'Функция не найдена в коде',
                            'passed': False
                        })
                        continue
                    
                    func = exec_globals[func_name]
                    result = func(test['input'])
                    
                    # Сравниваем результат
                    if isinstance(test['expected'], float):
                        passed = abs(result - test['expected']) < 0.001
                    else:
                        passed = result == test['expected']
                    
                    results.append({
                        'input': test['input'],
                        'expected': test['expected'],
                        'actual': result,
                        'passed': passed
                    })
                    
                except Exception as e:
                    results.append({
                        'input': test['input'],
                        'error': str(e),
                        'passed': False
                    })
            
            if temp_file and os.path.exists(temp_file):
                os.unlink(temp_file)
                
            return results
            
        except Exception as e:
            if temp_file and os.path.exists(temp_file):
                os.unlink(temp_file)
            return [{'error': str(e), 'passed': False}]

@challenges_bp.route('/challenge/<int:level>')
def get_challenge(level):
    challenge_system = CodeChallenge()
    challenge = challenge_system.challenges.get(level)
    if not challenge:
        return jsonify({'error': 'Challenge not found'}), 404
    return jsonify(challenge)

@challenges_bp.route('/challenge/<int:level>/submit', methods=['POST'])
def submit_challenge(level):
    data = request.json
    code = data.get('code', '')
    
    challenge_system = CodeChallenge()
    challenge = challenge_system.challenges.get(level)
    if not challenge:
        return jsonify({'error': 'Challenge not found'}), 404
    
    results = challenge_system.run_python_code(code, challenge['tests'])
    passed = all(r.get('passed', False) for r in results if 'passed' in r)
    
    return jsonify({
        'passed': passed,
        'results': results,
        'message': '🎉 Поздравляем! Задание выполнено!' if passed else '❌ Попробуйте еще раз! Проверьте логику вашего решения.'
    })