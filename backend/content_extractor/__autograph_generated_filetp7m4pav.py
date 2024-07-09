# coding=utf-8
def outer_factory():

    def inner_factory(ag__):

        def tf__call(self, inputs, **kwargs):
            with ag__.FunctionScope('call', 'fscope', ag__.STD) as fscope:
                do_return = False
                retval_ = ag__.UndefinedReturnValue()
                (source, target) = ag__.ld(inputs)
                target_shape = ag__.converted_call(ag__.ld(keras).backend.shape, (ag__.ld(target),), None, fscope)

                def get_state():
                    return (do_return, retval_)

                def set_state(vars_):
                    nonlocal do_return, retval_
                    (do_return, retval_) = vars_

                def if_body():
                    nonlocal do_return, retval_
                    raise ag__.ld(NotImplementedError)

                def else_body():
                    nonlocal do_return, retval_
                    try:
                        do_return = True
                        retval_ = ag__.converted_call(ag__.ld(tf).compat.v1.image.resize_bilinear, (ag__.ld(source),), dict(size=(ag__.ld(target_shape)[1], ag__.ld(target_shape)[2]), half_pixel_centers=True), fscope)
                    except:
                        do_return = False
                        raise
                ag__.if_stmt(ag__.converted_call(ag__.ld(keras).backend.image_data_format, (), None, fscope) == 'channels_first', if_body, else_body, get_state, set_state, ('do_return', 'retval_'), 2)
                return fscope.ret(retval_, do_return)
        return tf__call
    return inner_factory