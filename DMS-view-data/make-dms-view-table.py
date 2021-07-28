


import phippery
from phippery.utils import *
from phippery.tidy import tidy_ds

sample_groups = {
    "Cohort 1 - Moderna Vaccinated #1" : ['M01', 'M02', 'M03', 'M04', 'M05', 'M06'],
    "Cohort 1 - Moderna Vaccinated #2" : ['M07', 'M08', 'M09', 'M10', 'M11', 'M12'],
    "Cohort 1 - Moderna Vaccinated #3" : ['M13', 'M14', 'M15', 'M16', 'M17', 'M18'],
    "Cohort 1 - Moderna Vaccinated #4" : ['M19', 'M20', 'M21', 'M22', 'M23', 'M24'],
    "Cohort 1 - Moderna Vaccinated #5" : ['M25', 'M26', 'M27', 'M28', 'M29', 'M30'],
    "Cohort 1 - Moderna Vaccinated #6" : ['M31', 'M32', 'M33', 'M34', 'M35', 'M36'],
    "Cohort 1 - Moderna Vaccinated #7" : ['M37', 'M38', 'M39', 'M40', 'M41', 'M42'],
    "Cohort 1 - Moderna Vaccinated #8" : ['M43', 'M44', 'M45', 'M46', 'M47', 'M48', 'M49'],
    "Cohort 2 - Infected to Vacc #1" : ['103C', '10C', '110C', '118C', '120C', '136C'],
    "Cohort 2 - Infected to Vacc #2" : ['146C', '149C', '154C', '161C', '163C', '191C'],
    "Cohort 2 - Infected to Vacc #3" : ['194C', '210C', '213C', '217C', '238C', '239C'],
    "Cohort 2 - Infected to Vacc #4" : ['242C', '24C', '26C', '79C'],
    "Cohort 2 - Healthy to Vacc #1" :['12H', '16H', '20H', '24H', '27H', '35H'],
    "Cohort 2 - Healthy to Vacc #2" :['36H', '38H', '3H', '4H', '50H', '53H', '54H'],
    "Cohort 2 - Healthy to Vacc #3" :['55H', '56H', '58H', '59H', '65H', '67H', '75H'],
    "Cohort 2 - hospitalized #1": ['12001', '12004', '12101', '12104', '6', '6C'], 
    "Cohort 2 - convalescent only #1": ['1', '2', '3', '4', '5'],
    "Cohort 2 - convalescent only #2": ['7', '8', '9', '10', '11', '12'],
    "Cohort 2 - convalescent only #3": ['13', '14', '15', '16', '17', '18']
}

# load the dataset post stats computation
#ds = phippery.load("../_ignore/curated-samples-06-29-21-bowtie2-layered.phip")
ds = phippery.load("../nextflow-pipeline-config/test-output/layered-analysis.phip")
st = ds.sample_table.to_pandas()
st.loc[st[st["visit_number"]=="9"].index, "visit_number"] = "36 Days post-vaccination"
st.loc[st[st["visit_number"]=="12"].index, "visit_number"] = "119 Days post-vaccination"
ds["sample_table"] = xr.DataArray(st, dims=ds.sample_table.dims)

pt = ds.peptide_table.to_pandas()
site_wt = {row["Loc"]: row["aa_sub"] for idx, row in pt.iterrows() if row["is_wt"]==True}

for group_name, group_pars in sample_groups.items():
    
    group_ids = id_coordinate_subset(ds, where="participant_ID", is_in=group_pars)
    ds_sub = ds.loc[dict(sample_id=group_ids)]
    print(ds_sub)
 
    condition_dfs = []
    condition_groupby = ["participant_ID", "library_batch", "visit_number"]
    for condition, condition_ds in phippery.iter_sample_groups(ds_sub, condition_groupby):
        ds_slim = condition_ds.loc[dict(sample_metadata=["sample_group"])]
        slim_tall = tidy_ds(ds_slim)

        wt = [site_wt[site] for site in slim_tall["Loc"]]
        pro = ["A B C" for i in range(len(slim_tall))]
        cond = [", ".join(condition) for i in range(len(slim_tall))] 
        condition_dfs.append(
            pd.DataFrame({
                'site': slim_tall["Loc"],
                'protein_site': slim_tall["Loc"],
                'label_site': slim_tall["Loc"],
                'site_WT_enrichment': slim_tall["counts_enrichment"],
                'mut_scaled_diff_sel': slim_tall["smooth_flank_1_enr_diff_sel"],
                'mutation': slim_tall["aa_sub"],
                'wildtype': wt,
                'protein_chain': pro,
                'condition': cond
            })
        )

    from functools import reduce
    merged_samples_df = reduce(
        lambda l, r: l.append(r, ignore_index=True, verify_integrity=False),
        condition_dfs,
    )
    saveto = "-".join(group_name.split())
    merged_samples_df.to_csv(f"{saveto}.csv", index=False)








