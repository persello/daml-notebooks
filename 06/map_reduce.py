# simulates a map/reduce BigData pipeline
# the mapper function is supposed to take some content and to transform it in a sequence of tuples (k, v)
# the reducer function is supposed to take a single key and an iterable of tuples having that key and return
# a new sequence of tuples (k, v)
# k must be a hashable type, whereas v can be any type

from typing import Callable, Any, Iterable, Tuple, Hashable
from collections import defaultdict
from multiprocessing.pool import ThreadPool
from functools import reduce
import logging
from typeguard import typechecked
from operator import iconcat
from functools import reduce

logger = logging.getLogger('map_reduce')
logging.basicConfig(level=logging.NOTSET)

@typechecked
def map_reduce(mapper: Callable[[Any], Iterable[Tuple[Hashable, Any]]], 
               reducer: Callable[[Hashable, Iterable[Any]], Iterable[Any]]):

    def accumulate(acc, x):
        if type(x) == list:
            return acc + x 
        elif type(x) == tuple:
            return acc + [x]
    def apply(items: Iterable[Any],
              log: bool = False):

        def partition(mapped_values):
            p = defaultdict(list)
            for key, value in map_result:
                p[key].append(value)
            return p
        
        if log:
            logger.setLevel(logging.INFO)
        else:
            logger.setLevel(logging.WARNING)
        tp = ThreadPool()
        logger.info(f'Using a thread pool with {len(tp._pool)} workers')
        logger.info('Running mappers (in parallel) and accumulating the results')
        map_result = reduce(accumulate, tp.map(mapper, items), [])
        logger.info(f'Result of the mappers: {map_result}')
        logger.info('Running the reducers (in parallel) and accumulating the results')        
        result = reduce(accumulate, tp.map(lambda t: reducer(*t), partition(map_result).items()), [])
        logger.info(f'Final result {result}')
        return result    
    
    return apply