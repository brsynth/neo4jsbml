import logging
from typing import Any, Dict, List

import libsbml
from neo4jsbml import relationship


class Sbml(object):
    def __init__(self, id: str, path: str, modelisation: str):
        self.id = id
        self.document = self.load_document(path=path)
        self.modelisation = modelisation
        self.model = self.document.getModel()
        if self.model is None:
            logging.error("No model found")
            raise ValueError

    @classmethod
    def sbase_to_dict(cls, sbase) -> Dict[Any, Any]:
        return dict(
            id_attribute=sbase.getIdAttribute(),  #  SId, optional
            name=sbase.getName(),  #  string, optional
            metaid=sbase.getMetaId(),  #  ID, optional
        )

    @classmethod
    def format_results(cls, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        for ix, result in enumerate(results):
            keys = []
            for k, v in result.items():
                if v is None or v == "":
                    keys.append(k)
            for k in keys:
                del result[k]
            results[ix] = result
        return results

    # Entities
    def get_document(self) -> List[Dict[str, Any]]:
        data = Sbml.sbase_to_dict(sbase=self.document)
        # TODO: get xmlns
        data.update(dict(
            annotation=self.document.getAnnotationString(),
            notes=self.document.getNotesString(),
            version=self.document.getVersion(),
            level=self.document.getLevel(),
            ))
        data["id"] = self.id
        return Sbml.format_results([data])

    def get_model(self) -> List[Dict[str, Any]]:
        data = Sbml.sbase_to_dict(sbase=self.model)
        if data.get("id") is None:
            data["id"] = self.id
        return Sbml.format_results([data])

    def get_compartments(self) -> List[Dict[str, Any]]:
        res = []
        for c in self.model.getListOfCompartments():
            data = Sbml.sbase_to_dict(sbase=c)
            data_c = dict(
                id=c.getId(),  #  SId, required
                spatial_dimensions=c.getSpatialDimensions(),  #  double, optional
                size=c.getSize(),  #  double, optional
                units=c.getUnits(),  #  UnitSIdRef, optional
                constant=c.getConstant(),  #  boolean
            )
            data.update(data_c)
            res.append(data)
        return Sbml.format_results(res)

    def get_species(self) -> List[Dict[str, Any]]:
        res = []
        for s in self.model.getListOfSpecies():
            data = Sbml.sbase_to_dict(sbase=s)
            data_specie = dict(
                id=s.getId(),  #  SId required
                initial_amount=s.getInitialAmount(),  #  double, optional
                initial_concentration=s.getInitialConcentration(),  #  double, optional
                substance_units=s.getSubstanceUnits(),  #  UnitSIdRef, optional
                has_only_substance_units=s.getHasOnlySubstanceUnits(),  #  boolean
                boundary_condition=s.getBoundaryCondition(),  #  boolean
                constant=s.getConstant(),  #  boolean
                conversion_factor=s.getConversionFactor(),  # SIdRef, optional
            )
            data.update(data_specie)
            res.append(data)
        return Sbml.format_results(res)

    def get_reactions(self) -> List[Dict[str, Any]]:
        res = []
        for r in self.model.getListOfReactions():
            data = dict(id=r.getId())
            res.append(data)
        return Sbml.format_results(res)

    def get_parameters(self) -> List[Dict[str, Any]]:
        res = []
        for p in self.model.getListOfParameters():
            data = Sbml.sbase_to_dict(sbase=p)
            data_p = dict(
                id=p.getId(),  #  SId, required
                value=p.getValue(),  #  double, optional
                units=p.getUnits(),  #  UnitSIdRef, optional
                constant=p.getConstant(),  #  boolean
            )
            data.update(data_p)
            res.append(data)
        return Sbml.format_results(res)

    """
    def get_genes(self) -> pd.DataFrame:
        res = []
        fbc = model.getPlugin('fbc')
        for g in fbc.getListOfGeneProducts():
            data = sbase_to_dict(s)
            data_gene = dict(
                id=g.getId(),  #  SId required
                label=g.getLabel(),
                name=g.getName(),
                metaid=g.getMetaId(),
                sboterm=g.getSBOTerm(),
            )
            data.update(data_gene)
            res.append(data)
        return Sbml.format_results(res)
    """

    # Relationships
    def get_relationships_document_model(self) -> List[Any]:
        res = []
        res.append(relationship.Relationship(left="Document", left_id=self.id, right="Model", right_id=self.model.getId(), relationship="HAS_MODEL"))
        return res

    def get_relationships_species_compartments(self) -> List[Any]:
        res = []
        for s in self.model.getListOfSpecies():
            res.append(relationship.Relationship(left="Species", left_id=s.getId(), right="Compartment", right_id=s.getCompartment(), relationship="HAS_COMPARTMENT"))
        return res

    def get_relationships_model_reactions(self) -> List[Any]:
        res = []
        for r in self.model.getListOfReaction():
            res.append(relationship.Relationship(left="Model", left_id=self.model.getId(), right="Reaction", right_id=r.getId(), relationship="HAS_REACTION"))
        return res

    def get_relationships_model_compartments(self) -> List[Any]:
        res = []
        for c in self.model.getListOfCompartment():
            res.append(relationship.Relationship(left="Model", left_id=self.model.getId(), right="Compartment", right_id=c.getId(), relationship="HAS_COMPARTMENT"))
        return res

    def get_relationships_model_parameters(self) -> List[Any]:
        res = []
        for p in self.model.getListOfParameter():
            res.append(relationship.Relationship(left="Model", left_id=self.model.getId(), right="Parameter", right_id=p.getId(), relationship="HAS_CONVERSION_FACTOR"))
        return res

    def get_relationships_species_reactions(self) -> List[Any]:
        res = []
        for r in self.model.getListOfReaction():
            # Products
            for p in r.getListOfProducts():
                data = dict(
                    stoichiometry=p.getStoichiometry(),  #  double, optional
                    constant=p.getConstant(),  #  boolean
                )
                res.append(relationship.Relationship(left="Reaction", left_id=r.getId(), right="Species", right_id=p.getSpecies(), relationship="HAS_PRODUCT", attributes=data))
            # Reactants
            for re in r.getListOfReactants():
                data = dict(
                    stoichiometry=re.getStoichiometry(),  #  double, optional
                    constant=re.getConstant(),  #  boolean
                )
                res.append(relationship.Relationship(left="Species", left_id=re.getSpecies(), right="Reaction", right_id=r.getId(), relationship="IS_REACTANT", attributes=data))
        return res

    def has_plugin(self) -> bool:
        pass

    """
    def get_relation(self):
        # Genes
        data_genes = dict(type_referene="gene_product")
        data_genes.update(data)
        fbc = r.getPlugin("fbc")
        gene_product_association = fbc.getGeneProductAssociation()
        if gene_product_association is None:
            data_genes["gene_product"] = []
        else:
            gene_association = compute_gene_associations(
                list(gene_product_association.all_elements)
            )

            fmt = fmt_gpa(gene_association)
            index = [0]
            if type(fmt) == list:
                index = [x for x in range(len(fmt))]
            data_genes["gene_product"] = fmt
            df = pd.concat([df, pd.DataFrame(data_genes, index=index)])
    """
    @classmethod
    def load_document(cls, path: str) -> Any:
        doc = libsbml.readSBML(path)
        errors = doc.getNumErrors()
        if errors > 0:
            logging.error(doc.printErrors())
            raise ValueError("Error when parsing SBML -> abort")
        return doc

