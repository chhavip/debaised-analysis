"""
Copyright 2020 Google LLC

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

https://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

"""This module contains the slice-compare intent.
The slice-compare intent can give the result so that user can easily
compare the data according to the way user want.
Also it supports some operations like cropping based on date range, 
slicing(removing rows that do not follow the conditions), group by.
Some of the operations are optional.
"""

from util import aspects

def slice_compare(table, metric, dimensions, slices, slice_compare_column, 
                                            summary_operator, **kwargs):
    """This function will implement the slice-compare intent

    Also removes the tuples that do not lie in the given date range.
    The arguments 'table, metric,dimension,slices, slices_compare_column, 
    summary_operator' are not optional, so they are passed as it is,
    'date_range' will be passed in kwargs.
    If some the optional args are None(not passed),
    it is assumed that we don't have to apply them.

    Args:
        table: Type-pandas.dataframe
            It has the contents of the csv file
        metric: Type-string
            It is the name of the column according to which we have group to be done,
            summary operator is applied on metric. Metric could a column
            containing strings, if we are applying count operator on it.
        dimensions: Type-list of str
            It is the name of column we want.
            In query:'top 5 batsman according to runs', dimension is 'batsman'.
            When summary_operator is not None, we group by dimensions.
        date_range: Type-tuple
            Tuple of start_date and end_date
        date_column_name: Type-str
            It is the name of column which contains date
        date_format: Type-str
            It is required by datetime.strp_time to parse the date in the format
            Format Codes
https://docs.python.org/3/library/datetime.html#strftime-and-strptime-behavior
        slices: Type-dictionary (will be changed)
            contains the key as column name and value as instance we want
            to slice
        slice_compare_column: Type-list of string
            first element denotes the column name by which we will do comparision.
            rest elements will the value belongs to that column by which we
            will compare the slices.
        summary_operator: Type-summary_operators enum members
            It denotes the summary operator, after grouping by dimensions.
            ex. SummaryOperators.MAX, SummaryOperators.SUM

    Note-summary_operator is always applied on metric column passed,
         and only when grouping is done

    Returns:
        The function will return the `table(a pandas dataframe object)`
        after applying the intent on the
        given `table(a pandas dataframe object)``

    """

    date_column_name = kwargs.get('date_column_name', 'date')
    date_range = kwargs.get('date_range', None)
    date_format = kwargs.get('date_format', 'yyyy-mm-dd')


    table = aspects.apply_date_range(table, date_range,
                                     date_column_name, date_format)

    table = aspects.slice_table(table, slices)

   # collecting the colums not to be removed
    required_columns = []
    if dimensions is not None:
        required_columns = dimensions.copy()
    required_columns.append(metric)

    table = aspects.crop_other_columns(table, required_columns)

    # slice_compare_column should be the last element of the group
    # so that groupby will show them together for every grouping
    dimensions.remove(slice_compare_column[0])
    dimensions.append(slice_compare_column[0])
    table = aspects.group_by(table, dimensions, summary_operator)

    return table
