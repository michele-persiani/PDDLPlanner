(define (domain ferry)

(:predicates
(not-eq ?a - object ?b - object)
(car ?a - object)
(location ?a - object)
(at-ferry ?a - object)
(at ?a - object ?b - object)
(empty-ferry)
(on ?a - object)
)

(:action sail_0
:parameters (?from - object ?to - object)
:precondition (and (not-eq ?from ?to) (location ?from) (location ?to) (at-ferry ?from))
:effect (and (at-ferry ?to) (not (at-ferry ?from)))
)

(:action board_1
:parameters (?car - object ?loc - object)
:precondition (and (car ?car) (location ?loc) (at ?car ?loc) (at-ferry ?loc) (empty-ferry))
:effect (and (on ?car) (not (at ?car ?loc)) (not (empty-ferry)))
)

(:action debark_2
:parameters (?car - object ?loc - object)
:precondition (and (car ?car) (location ?loc) (on ?car) (at-ferry ?loc))
:effect (and (at ?car ?loc) (empty-ferry) (not (on ?car)))
)
)