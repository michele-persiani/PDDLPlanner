(define (problem ferryproblem)
(:domain ferry)
(:objects 
l0 l1 l2 l3 c0 c1 c2 c3 c4 c5 c6 c7 - object
)

(:init 
(car c1)
(empty-ferry)
(not-eq l3 l1)
(not-eq l0 c0)
(not-eq l3 c3)
(not-eq l1 l0)
(not-eq l1 l2)
(not-eq l0 l2)
(not-eq l3 l2)
(car c3)
(location l3)
(at c0 l1)
(not-eq l0 l3)
(at c4 l0)
(not-eq l2 l0)
(not-eq l2 l3)
(at c2 l3)
(car c6)
(not-eq l0 l1)
(location l2)
(on c5)
(at c6 l3)
(not-eq l1 l3)
(at c5 l3)
(at c7 l3)
(not-eq l3 l0)
(car c2)
(at c1 l3)
(at-ferry l2)
(car c5)
(at c3 l1)
(location l0))

(:goal 
(and (at c3 l3) (at c7 l1) (at c1 l2) (at c2 l3) (at c3 l3) (at c4 l1)))



)