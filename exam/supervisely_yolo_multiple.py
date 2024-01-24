#      This program is free software: you can redistribute it and/or modify
#      it under the terms of the GNU General Public License as published by
#      the Free Software Foundation, either version 3 of the License, or
#      (at your option) any later version.
#
#      This program is distributed in the hope that it will be useful,
#      but WITHOUT ANY WARRANTY; without even the implied warranty of
#      MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#      GNU General Public License for more details.
#
#      You should have received a copy of the GNU General Public License
#      along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#      Author = "Namik Delilovic"
#      Contact = "namikdelilovic@gmail.com"
#      License = "GPLv3"
#      Version = "0.9"
#      Date = "2019/10/09"

import glob
import json
import optparse
import os
from shutil import copyfile


class S2Y:
    def __init__(self, supervisely_path: str, yolo_path: str, skip_copy: bool = False):
        self.supervisely_path = supervisely_path
        self.yolo_path = yolo_path
        self.skip_copy = skip_copy

    def get_class_names_from_supervisely(self):
        class_names_array = []
        class_names_path = self.supervisely_path + "//meta.json"
        with open(class_names_path, "r") as file:
            json_classes = json.load(file)["classes"]
            for json_class in json_classes:
                class_names_array.append(json_class["title"])
        return class_names_array

    def create_yolo_file_structure(self):
        os.makedirs(os.path.dirname(self.yolo_path + "//labels//"), exist_ok=True)
        os.makedirs(os.path.dirname(self.yolo_path + "//images//"), exist_ok=True)

    def create_class_file(self, class_names_array):
        class_file_path = self.yolo_path + "//labels//classes.txt"
        with open(class_file_path, "w") as f:
            for class_name in class_names_array:
                f.write("%s\n" % class_name)

    def get_yolo_annotation_info(self, folder_name, file_name, class_names_array):
        image_path = self.supervisely_path + "/" + folder_name + "//img//" + file_name
        print("image_path", image_path)

        image_json_file = (
            self.supervisely_path + "/" + folder_name + "//ann//" + file_name + ".json"
        )
        with open(image_json_file, "r") as file:
            json_object = json.load(file)

        class_coord_list = []

        class_id = 0
        if len(json_object["objects"]) > 0:
            if not self.skip_copy:
                copy_path = (
                    self.yolo_path
                    + "//images//"
                    + folder_name
                    + "_"
                    + os.path.basename(image_path)
                )
                print("copy_path", copy_path)
                copyfile(image_path, copy_path)
            else:
                move_path = (
                    self.yolo_path
                    + "//images//"
                    + folder_name
                    + "_"
                    + os.path.basename(image_path)
                )
                print("move_path", move_path)
                os.rename(image_path, move_path)

            for obj in json_object["objects"]:
                points = obj["points"]["exterior"]
                w = json_object["size"]["width"]
                h = json_object["size"]["height"]
                w_point = points[1][0] - points[0][0]
                h_point = points[1][1] - points[0][1]
                x1 = round((points[0][0] + w_point / 2) / w, 5)
                y1 = round((points[0][1] + h_point / 2) / h, 5)
                x2 = round(w_point / w, 5)
                y2 = round(h_point / h, 5)
                class_id = class_names_array.index(obj["classTitle"])

                class_coord_list.append(
                    {"class_id": class_id, "x1": x1, "y1": y1, "x2": x2, "y2": y2}
                )

        return class_coord_list  # class_id, x1, y1, x2, y2

    def create_text_file(self, folder_name, file_name, class_names_array):
        # class_id, x1, y1, x2, y2 = S2Y.get_yolo_annotation_info(folder_name, file_name, class_names_array)
        class_coord_list = self.get_yolo_annotation_info(
            folder_name, file_name, class_names_array
        )
        print("class_coord_list", class_coord_list)

        if len(class_coord_list) > 0:
            text_file_path = (
                self.yolo_path
                + "//labels//"
                + os.path.splitext(folder_name + "_" + file_name)[0]
                + ".txt"
            )
            with open(text_file_path, "w") as text_file:
                for coord in class_coord_list:
                    class_id = coord["class_id"]
                    x1 = coord["x1"]
                    y1 = coord["y1"]
                    x2 = coord["x2"]
                    y2 = coord["y2"]

                    text_file.write("{} {} {} {} {}".format(class_id, x1, y1, x2, y2))
                    text_file.write("\n")
