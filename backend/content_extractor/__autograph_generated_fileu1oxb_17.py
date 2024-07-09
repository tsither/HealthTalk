# coding=utf-8
def outer_factory():

    def inner_factory(ag__):

        def tf__call(self, x: List[tf.Tensor], **kwargs: Any) -> tf.Tensor:
            with ag__.FunctionScope('call', 'fscope', ag__.STD) as fscope:
                do_return = False
                retval_ = ag__.UndefinedReturnValue()
                results = [ag__.converted_call(ag__.ld(block), (ag__.ld(fmap),), dict(**ag__.ld(kwargs)), fscope) for (block, fmap) in ag__.converted_call(ag__.ld(zip), (ag__.ld(self).inner_blocks, ag__.ld(x)), None, fscope)]

                def get_state():
                    return ()

                def set_state(block_vars):
                    pass

                def loop_body(itr):
                    idx = itr
                    ag__.ld(results)[ag__.ld(idx)] += ag__.converted_call(ag__.ld(self).upsample, (ag__.ld(results)[ag__.ld(idx) + 1],), None, fscope)
                idx = ag__.Undefined('idx')
                ag__.for_stmt(ag__.converted_call(ag__.ld(range), (ag__.converted_call(ag__.ld(len), (ag__.ld(results),), None, fscope) - 1, -1), None, fscope), None, loop_body, get_state, set_state, (), {'iterate_names': 'idx'})
                results = [ag__.converted_call(ag__.ld(block), (ag__.ld(fmap),), dict(**ag__.ld(kwargs)), fscope) for (block, fmap) in ag__.converted_call(ag__.ld(zip), (ag__.ld(self).layer_blocks, ag__.ld(results)), None, fscope)]
                try:
                    do_return = True
                    retval_ = ag__.converted_call(ag__.ld(layers).concatenate, (ag__.ld(results),), None, fscope)
                except:
                    do_return = False
                    raise
                return fscope.ret(retval_, do_return)
        return tf__call
    return inner_factory