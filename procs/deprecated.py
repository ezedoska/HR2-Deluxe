# stats_prov = sqldf(
#     """
#                 SELECT
#                 [ PROV_ACTIVIDAD  ] as PROVINCIA,
#                 [ LOCALIDAD  ] as LOCALIDAD,
#                 [SEXO],
#                 COUNT(DISTINCT d.[id_persona ]) as EFECTORES,
#                 COUNT(DISTINCT p.id_persona)    as PNC,
#                 COUNT(DISTINCT j.id_persona)    as JUB_PEN,
#                 COUNT(DISTINCT e.id_persona)    as EMPLEO_DEP,
#                 COUNT(DISTINCT a.id_persona)    as ASIG_FAM,
#                 COUNT(DISTINCT f.id_persona)    as FALLECIDOS,
#                 COUNT(DISTINCT h.id_persona)    as JURIDICAS,
#                 COUNT(DISTINCT r.id_persona)    as RUBPS
#                 FROM      var d
#                 LEFT JOIN pnc p on p.id_persona = d.[id_persona ]
#                 LEFT JOIN jub j on j.id_persona = d.[id_persona ]
#                 LEFT JOIN dep e on e.id_persona = d.[id_persona ]
#                 LEFT JOIN asg a on a.id_persona = d.[id_persona ]
#                 LEFT JOIN fal f on f.id_persona = d.[id_persona ]
#                 LEFT JOIN jur h on h.id_persona = d.[id_persona ]
#                 LEFT JOIN rub r on r.id_persona = d.[id_persona ]
#                 GROUP BY [ PROV_ACTIVIDAD  ],[ LOCALIDAD  ], [SEXO]
#               """
# )
# stats_prov.set_index("PROVINCIA", inplace=True)
# stats_prov.loc["TOTAL"] = stats_prov.sum(numeric_only=True)
# stats_prov.to_csv("Stats_por_provincia.txt", sep="\t")

# muebles = sqldf(
#     """
#                 select * from aut
#                 where ID_PERSONA IN (
#                 select dat.id_persona
#                 from dat inner join
#                 aut on aut.ID_PERSONA=dat.id_persona
#                 GROUP BY dat.id_persona
#                 HAVING COUNT(DOMINIO)>2)
#                 ORDER BY ID_PERSONA"""
# )
# muebles.set_index("ID_PERSONA", inplace=True)

# inmuebles = sqldf(
#     """
#                 select * from inm
#                 where ID_PERSONA IN (
#                 select id_persona
#                 from inm
#                 GROUP BY id_persona
#                 HAVING COUNT(ID_PERSONA)>1)
#                 ORDER BY ID_PERSONA"""
# )
# inmuebles.set_index("ID_PERSONA", inplace=True)

# eval = sqldf(
#     """
#             SELECT
#             distinct(dat.id_persona),
#             dat.cuit,
#             dat.ndoc,
#             dat.deno,
#             case when dat.sexo=1 then 'M' else 'F' end as sexo,
#             dat.fnac,
#             dat.grado_confiab,
#             case when inm.id_persona is not null then 'Si' else 'No' end as Inmuebles,
#             case when aut.id_persona is not null then 'Si' else 'No' end as Muebles,
#             case when dep.base=105 then 'Si' else 'No' end as Servicio_Domestico,
#             case when dep.monto > 45000 then 'Si' else 'No' end as Dependiente,
#             case when jur.id_persona is not null then 'Si' else 'No' end as Juridicas,
#             case when jub.monto > 45000 then 'Si' else 'No' end as Jub_pen,
#             case when fal.id_persona is not null then 'Si' else 'No' end as Fallecido
#             from dat
#             left join muebles aut on aut.ID_PERSONA = dat.id_persona
#             left join inmuebles inm on inm.ID_PERSONA = dat.id_persona
#             left join dep on dep.ID_PERSONA = dat.id_persona
#             left join jub on jub.ID_PERSONA = dat.id_persona
#             left join jur on jur.ID_PERSONA = dat.id_persona
#             left join fal on fal.ID_PERSONA = dat.id_persona
#             where
#             Inmuebles ='Si'
#             or Muebles ='Si'
#             or Servicio_Domestico ='Si'
#             or Dependiente ='Si'
#             or Juridicas ='Si'
#             or Jub_pen ='Si'
#             or Fallecido='Si'
#                 """
# )
