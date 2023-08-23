# -*- coding: utf-8 -*-

# Copyright 2023 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

from typing import List, Any, Union
from enum import Enum

try:
    import pandas as pd

    PandasData = pd.DataFrame
except ImportError:
    pd = None
    PandasData = Any

df_restore_func_metadata_key = "restore_df_actions"
df_restore_func_args_metadata_key = "restore_df_actions_args"


class ActionType(str, Enum):
    CAST_COL_NAME = "CAST_COL_NAME"
    CAST_ROW_INDEX = "CAST_ROW_INDEX"
    CAST_CATEGORICAL = "CAST_CATEGORICAL"


class _Helper:
    def __init__(self):
        if not pd:
            raise ImportError(
                "pandas is not installed and required for Pandas Serializer."
            )
        self.restore_df_actions = []
        self.restore_df_actions_args = []
        self.restore_func_metadata_key = "restore_df_actions"
        self.restore_func_args_metadata_key = "restore_df_actions_args"

    def create_placeholder_col_names(self, df: PandasData):
        """Creates placeholder column names for dataframes without column names.

        Args:
            df (pd.DataFrame):
                Required. This is the dataframe to serialize.
        """
        if isinstance(df.columns, pd.RangeIndex):
            df.columns = [str(x) for x in df.columns]
            self.restore_df_actions.append("remove_placeholder_col_names")
            self.restore_df_actions_args.append([])

    def remove_placeholder_col_names(self, df: PandasData):
        df.columns = pd.RangeIndex(start=0, stop=len(df.columns), step=1)

    def _append_to_temp_indices(
        self, temp_indices: List[str], name: Any, action: ActionType
    ):
        """
        This function is a helper for the cast_int_to_str function.

        Args:
            temp_indices (List[str]): a temporary array of indices that keeps track
            of the original values of the column or row indices.

            name (Any): the name of the column or row. Note that this could be any type,
            but Vertex only handles integer-to-string casting. Users who attempt to
            serialize Pandas dataframes with non-string or non-integer column/row indices
            will encounter a runtime error from pyarrow.

            action (ActionType): the enum that tells the deserialization function
            at runtime whether a row or a column index is being cast back.
        """
        if isinstance(name, int):
            temp_indices.append(str(name))
            self.restore_df_actions.append("cast_str_to_int")
            self.restore_df_actions_args.append([action, str(name)])
        else:
            temp_indices.append(name)

    def cast_int_to_str(self, df: PandasData, action: ActionType):
        """
        This function casts integers to strings depending on the action type.

        In the cases of casting integer-indexed columns or rows, the function
        will modify the dataframe and append to restore_df_actions that will cast
        the column and row indices back to their original data types.

        In the case of handling categorical columns, the function will keep track
        of the column names with integers being the primitive data type, preserve
        their orders if the column is ordered, and add relevant metadata to the
        restore_df_actions and restore_df_actions_args arrays.

        Args:
            df (pd.DataFrame):
                Required. This is the dataframe to serialize.
            action (enum.Enum):
                Required. One of [CAST_COL_NAME, CAST_ROW_NAME, CAST_CATEGORICAL]
        """
        temp_indices = []
        if action == ActionType.CAST_COL_NAME:
            for i in range(len(df.columns)):
                self._append_to_temp_indices(temp_indices, df.columns[i], action)
            df.columns = temp_indices
        elif action == ActionType.CAST_ROW_INDEX:
            for i in range(len(df.index)):
                self._append_to_temp_indices(temp_indices, df.index[i], action)
            df.index = temp_indices
        elif action == ActionType.CAST_CATEGORICAL:
            columns_to_cast = []
            column_orders = []
            columns_to_reorder = []
            for col_name in df.select_dtypes(include=["category"]):
                if df[col_name].cat.ordered:
                    column_orders.append(df[col_name].cat.categories.values.tolist())
                    columns_to_reorder.append(col_name)
                # cast the columns with integers as categories
                try:
                    int(df.at[df[col_name].first_valid_index(), col_name])
                    columns_to_cast.append(col_name)
                # pass on the columns that are non-integers
                except ValueError:
                    pass
            self.restore_df_actions.append("restore_category_order")
            self.restore_df_actions_args.append([columns_to_reorder, column_orders])

            self.restore_df_actions.append("cast_str_to_int")
            self.restore_df_actions_args.append([action, columns_to_cast])

    @staticmethod
    def cast_str_to_int(
        df: PandasData,
        action: ActionType,
        index_name_or_columns: Union[List[str], str] = None,
    ):
        """
        This function is used by the deserialization function to undo any temp
        workarounds applied to the dataframe during serialization.

        Args:
            df （pd.DataFrame):
                Required. This is the dataframe to deserialize.
            action (enum.Enum):
                Required. One of [CAST_COL_NAME, CAST_ROW_NAME, CAST_CATEGORICAL]
            index_name_or_columns (Union[List[str], str]):
                Required. This is the list of index names to cast back to int
                in the case of restoring row or column indices. In the case of
                categorical columns, this is the list of column names to restore.
        """
        restored_indices = []
        if action == ActionType.CAST_COL_NAME:
            for i in range(len(df.columns)):
                if df.columns[i] == index_name_or_columns:
                    restored_indices.append(int(index_name_or_columns))
                else:
                    restored_indices.append(df.columns[i])
            df.columns = restored_indices
        elif action == ActionType.CAST_ROW_INDEX:
            for i in range(len(df.index)):
                if df.index[i] == index_name_or_columns:
                    restored_indices.append(int(index_name_or_columns))
                else:
                    restored_indices.append(df.index[i])
            df.index = restored_indices
        elif action == ActionType.CAST_CATEGORICAL:
            for column in index_name_or_columns:
                df[column] = df[column].astype("int", errors="ignore")
                df[column] = df[column].astype("category")

    @staticmethod
    def restore_category_order(
        df: PandasData, columns: List[str], categories: List[Any]
    ):
        for (column, category) in zip(columns, categories):
            df[column] = df[column].cat.set_categories(
                new_categories=category, ordered=True
            )
