# global
import math

from hypothesis import given, strategies as st, assume

# local
import ivy_tests.test_ivy.helpers as helpers
from ivy_tests.test_ivy.helpers import handle_cmd_line_args


# diagflat
@st.composite
def _generate_diag_args(draw):
    x_shape = draw(
        helpers.get_shape(
            min_num_dims=1, max_num_dims=2, min_dim_size=1, max_dim_size=5
        )
    )

    flat_x_shape = math.prod(x_shape)

    dtype_x = draw(
        helpers.dtype_and_values(
            available_dtypes=helpers.get_dtypes("numeric"),
            shape=x_shape,
            min_value=-1e2,
            max_value=1e2,
        )
    )

    offset = draw(helpers.ints(min_value=-5, max_value=5))

    dtype = dtype_x[0]

    dtype_padding_value = draw(
        helpers.dtype_and_values(
            available_dtypes=dtype,
            max_dim_size=1,
            min_dim_size=1,
            min_num_dims=1,
            max_num_dims=1,
            min_value=-1e2,
            max_value=1e2,
        )
    )

    align = draw(
        st.sampled_from(["RIGHT_LEFT", "RIGHT_RIGHT", "LEFT_LEFT", "LEFT_RIGHT"])
    )

    if offset < 0:
        num_rows_is_negative = draw(st.booleans())
        if num_rows_is_negative:
            num_rows = -1
            num_cols = draw(
                st.one_of(
                    st.integers(min_value=-1, max_value=-1),
                    st.integers(min_value=flat_x_shape, max_value=50),
                )
            )
        else:
            num_rows_is_as_expected = draw(st.booleans())
            if num_rows_is_as_expected:
                num_rows = flat_x_shape + abs(offset)
                num_cols = draw(
                    st.one_of(
                        st.integers(min_value=-1, max_value=-1),
                        st.integers(min_value=flat_x_shape, max_value=50),
                    )
                )
            else:
                num_rows = draw(
                    st.integers(min_value=flat_x_shape + abs(offset) + 1, max_value=50)
                )
                num_cols = draw(st.sampled_from([-1, flat_x_shape]))
    if offset > 0:
        num_cols_is_negative = draw(st.booleans())
        if num_cols_is_negative:
            num_cols = -1
            num_rows = draw(
                st.one_of(
                    st.integers(min_value=-1, max_value=-1),
                    st.integers(min_value=flat_x_shape, max_value=50),
                )
            )
        else:
            num_cols_is_as_expected = draw(st.booleans())
            if num_cols_is_as_expected:
                num_cols = flat_x_shape + abs(offset)
                num_rows = draw(
                    st.one_of(
                        st.integers(min_value=-1, max_value=-1),
                        st.integers(min_value=flat_x_shape, max_value=50),
                    )
                )
            else:
                num_cols = draw(
                    st.integers(min_value=flat_x_shape + abs(offset) + 1, max_value=50)
                )
                num_rows = draw(st.sampled_from([-1, flat_x_shape]))

    if offset == 0:
        num_rows_is_negative = draw(st.booleans())
        num_cols_is_negative = draw(st.booleans())

        if num_rows_is_negative and num_cols_is_negative:
            num_rows = -1
            num_cols = -1

        if num_rows_is_negative:
            num_rows = -1
            num_cols = draw(
                st.integers(min_value=flat_x_shape + abs(offset), max_value=50)
            )

        if num_cols_is_negative:
            num_cols = -1
            num_rows = draw(
                st.integers(min_value=flat_x_shape + abs(offset), max_value=50)
            )

        else:
            num_rows_is_as_expected = draw(st.booleans())
            if num_rows_is_as_expected:
                num_rows = flat_x_shape
                num_cols = draw(
                    st.integers(min_value=flat_x_shape + abs(offset), max_value=50)
                )
            else:
                num_cols = flat_x_shape
                num_rows = draw(
                    st.integers(min_value=flat_x_shape + abs(offset), max_value=50)
                )

    return dtype_x, offset, dtype_padding_value, align, num_rows, num_cols


@handle_cmd_line_args
@given(
    args_packet=_generate_diag_args(),
    num_positional_args=helpers.num_positional_args(fn_name="diagflat"),
)
def test_diagflat(
    *,
    as_variable,
    with_out,
    num_positional_args,
    native_array,
    container,
    instance_method,
    fw,
    args_packet,
):
    dtype_x, offset, dtype_padding_value, align, num_rows, num_cols = args_packet

    x_dtype, x = dtype_x
    padding_value_dtype, padding_value = dtype_padding_value
    padding_value = padding_value[0][0]

    assume("float16" not in x_dtype)
    assume("bfloat16" not in x_dtype)

    helpers.test_function(
        input_dtypes=x_dtype + ["int64"] + padding_value_dtype,
        as_variable_flags=as_variable,
        with_out=with_out,
        num_positional_args=num_positional_args,
        native_array_flags=native_array,
        container_flags=container,
        instance_method=instance_method,
        fw=fw,
        fn_name="diagflat",
        x=x[0],
        offset=offset,
        padding_value=padding_value,
        align=align,
        num_rows=num_rows,
        num_cols=num_cols,
        atol_=1e-01,
        rtol_=1 / 64,
    )


# kron
@handle_cmd_line_args
@given(
    dtype_x=helpers.dtype_and_values(
        available_dtypes=helpers.get_dtypes("numeric"),
        min_num_dims=1,
        max_num_dims=3,
        min_dim_size=1,
        max_dim_size=3,
        num_arrays=2,
        shared_dtype=True,
    ),
    num_positional_args=helpers.num_positional_args(fn_name="kron"),
)
def test_kron(
    dtype_x,
    as_variable,
    with_out,
    num_positional_args,
    native_array,
    container,
    instance_method,
    fw,
):
    dtype, x = dtype_x
    helpers.test_function(
        input_dtypes=dtype,
        as_variable_flags=as_variable,
        with_out=with_out,
        num_positional_args=num_positional_args,
        native_array_flags=native_array,
        container_flags=container,
        instance_method=instance_method,
        fw=fw,
        fn_name="kron",
        a=x[0],
        b=x[1],
    )
