import os


def create_table(size):
    table_of_zeros = [[0] * size for _ in range(size)]
    return table_of_zeros


def remove_zero_rows_columns(matrix):

    num_rows = len(matrix)
    num_cols = len(matrix[0]) if num_rows > 0 else 0

    zero_rows = [i for i in range(num_rows) if all(matrix[i][j] == 0 for j in range(num_cols))]
    zero_cols = [j for j in range(num_cols) if all(matrix[i][j] == 0 for i in range(num_rows))]

    matrix = [row for i, row in enumerate(matrix) if i not in zero_rows]

    matrix = [[matrix[i][j] for j in range(num_cols) if j not in zero_cols] for i in range(len(matrix))]

    return matrix


def create_prediction_list(file_path):
    prediction_list = []

    with open(file_path, 'r') as file:
        for line in file:
            first_number = int(line.split()[0])
            prediction_list.append(first_number)

    return prediction_list


def check_rectangles_localization(line1, line2):
    elements1 = line1.split()
    elements2 = line2.split()
    box1 = [float(elements1[1]), float(elements1[2]), float(elements1[3]), float(elements1[4])]
    box2 = [float(elements2[1]), float(elements2[2]), float(elements2[3]), float(elements2[4])]

    x1, y1, w1, h1 = box1
    x2, y2, w2, h2 = box2

    x_intersection = max(x1, x2)
    y_intersection = max(y1, y2)
    w_intersection = min(x1 + w1, x2 + w2) - x_intersection
    h_intersection = min(y1 + h1, y2 + h2) - y_intersection

    if w_intersection <= 0 or h_intersection <= 0:
        return 0.0

    area_intersection = w_intersection * h_intersection
    area_union = w1 * h1 + w2 * h2 - area_intersection

    iou = area_intersection / area_union

    return iou


def if_txt_not_generated(table, file_txt_ground_truth):
    # Brak detekcji - brak pliku txt
    with open(file_txt_ground_truth, 'r') as f1:
        lines1 = f1.readlines()
        for line1 in lines1:
            number1 = int(line1.split()[0])
            table[number1][-1] += 1


def create_confusion_matrix(table, ground_truth_path, predictions_path):
    intersection_over_union, counter = 0, 0

    for file in os.listdir(ground_truth_path):
        if os.path.isfile(os.path.join(ground_truth_path, file)):
            file_txt_ground_truth = os.path.join(ground_truth_path, file)
            file_txt_predictions = os.path.join(predictions_path, file)

            if os.path.isfile(file_txt_predictions):
                with open(file_txt_ground_truth, 'r') as f1, open(file_txt_predictions, 'r') as f2:
                    lines1 = f1.readlines()
                    lines2 = f2.readlines()
                    prediction_list = create_prediction_list(file_txt_predictions)

                    for line1 in lines1:
                        number1 = int(line1.split()[0])
                        detected = False

                        for index, line2 in enumerate(lines2):
                            number2 = int(line2.split()[0])

                            iou = check_rectangles_localization(line1, line2)
                            iou_threshold = 0.5

                            if iou >= iou_threshold:
                                prediction_list.remove(number2)
                                detected = True

                                # Prawidłowa detekcja
                                if number1 == number2:
                                    intersection_over_union += iou
                                    counter += 1
                                    table[number1][number1] += 1

                                # Fałszywa detekcja pojazdu innej klasy
                                if number1 != number2:
                                    table[number1][number2] += 1

                            # Brak detekcji
                            if index == len(lines2) - 1 and detected is False:
                                table[number1][-1] += 1

                    # Fałszywe detekcje tła
                    for i in prediction_list:
                        table[-1][i] += 1

                    # Brak detekcji - pusty plik txt
                    if not lines2:
                        for line1 in lines1:
                            number1 = int(line1.split()[0])
                            table[number1][-1] += 1

            else:
                if_txt_not_generated(table, file_txt_ground_truth)

    return intersection_over_union / counter


def count_metrics(table):
    Tp, Tn, Fp, Fn = 0, 0, 0, 0

    for row_index, row in enumerate(table):
        for column_index, element in enumerate(row):
            if row_index == column_index:
                Tp += element
            if row_index != column_index and column_index != len(table) -1:
                Fp += element
            if row_index != column_index and row_index != len(table) -1:
                Fn += element

    precision = Tp / (Tp + Fp)
    recall = Tp / (Tp + Fn)
    accuracy = Tp / (Tp + Fp + Fn)

    return precision, recall, accuracy


# Przypisanie zmiennych
ground_truth_folder = r'Należy uzupełnić ścieżkę do folderu z labelami'
predictions_folder = r'Należy uzupełnić ścieżkę do folderu z labelami'

# Tworzenie macierzy
matrix_size = 10
confusion_matrix = create_table(matrix_size)

# Obliczenia
IoU = round(create_confusion_matrix(confusion_matrix, ground_truth_folder, predictions_folder), 2)
confusion_matrix = remove_zero_rows_columns(confusion_matrix)
precision, recall, accuracy = count_metrics(confusion_matrix)
precision = round(precision, 2)
recall = round(recall, 2)
accuracy = round(accuracy, 2)
F1_score = round(2 * (precision * recall) / (precision + recall), 2)

# Wyswietlenie wyników
for row in confusion_matrix:
    print(row)

print("Precision: ", precision, "%")
print("Recall: ", recall, "%")
print("Accuracy: ", accuracy, "%")
print("F1 score: ", F1_score, "%")
print("Intersection over Union: ", IoU, "%")
