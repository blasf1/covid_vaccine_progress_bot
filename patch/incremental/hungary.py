
import re

from bs4 import BeautifulSoup
import pandas as pd

from vax.utils.utils import get_soup, clean_string
from vax.utils.incremental import clean_count, merge_with_current_data
from vax.utils.dates import extract_clean_date


class Hungary:
    def __init__(self):
        self.source_url = "https://koronavirus.gov.hu"
        self.location = "Hungary"
        self._num_max_pages = 10
        self.regex = {
            "title": r"\d+ [millió]+ \d+ [ezer]+ a beoltott, \d+ az új fertőzött, elhunyt \d+ beteg",
            "metrics": (
                r"(?:A|a) beoltottak száma ([\d ]+)\s{1,2}(?:fő)?(?:, )?(?:közülük )?([\d ]+) fő már a második "
                r"oltását is megkapta."
            ),
        }

    def read(self, last_update: str) -> pd.DataFrame:
        data = []
        for cnt in range(0, self._num_max_pages):
            # print(f"page: {cnt}")
            url = f"{self.source_url}/hirek?page={cnt}/"
            soup = get_soup(url)
            data_, proceed = self.parse_data(soup, last_update)
            data.extend(data_)
            if not proceed:
                break
        return pd.DataFrame(data)

    def parse_data(self, soup: BeautifulSoup, last_update: str) -> tuple:
        elems = self.get_elements(soup)
        records = []
        for elem in elems:
            # print(elem["date"], elem)
            soup = get_soup(elem["link"])
            record = {
                "source_url": elem["link"],
                **self.parse_data_news_page(soup),
            }
            if record["date"] > last_update:
                # print(record["date"], record["people_vaccinated"], record["people_fully_vaccinated"], "added")
                records.append(record)
            else:
                # print(record["date"], "END")
                return records, False
        return records, True

    def get_elements(self, soup: BeautifulSoup) -> list:
        elems = soup.find_all("h3", text=re.compile(self.regex["title"]))
        elems = [{"link": self.parse_link(elem)} for elem in elems]
        return elems

    def parse_data_news_page(self, soup: BeautifulSoup):
        text = clean_string(soup.find(class_="page_body").text)
        match = re.search(self.regex["metrics"], text)
        metrics = {
            "people_vaccinated": clean_count(match.group(1)),
            "people_fully_vaccinated": clean_count(match.group(2)),
            "date": extract_clean_date(
                soup.find("p").text,
                regex="(202\d. .* \d+.) - .*",
                date_format="%Y. %B %d.",
                loc="hu_HU",
                minus_days=1,
            ),
        }
        return metrics

    def parse_link(self, elem):
        href = elem.parent["href"]
        return f"{self.source_url}/{href}"

    def pipe_drop_duplicates(self, df: pd.DataFrame) -> pd.DataFrame:
        return df.sort_values("date").drop_duplicates(
            subset=["people_vaccinated", "people_fully_vaccinated"], keep="first"
        )

    def pipe_location(self, df: pd.DataFrame) -> pd.DataFrame:
        return df.assign(location=self.location)

    def pipe_vaccine(self, df: pd.DataFrame) -> pd.DataFrame:
        return df.assign(
            vaccine="Johnson&Johnson, Moderna, Oxford/AstraZeneca, Pfizer/BioNTech, Sinopharm/Beijing, Sputnik V"
        )

    def pipe_select_output_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        return df[
            [
                "location",
                "date",
                "vaccine",
                "source_url",
                "people_vaccinated",
                "people_fully_vaccinated",
            ]
        ]

    def pipeline(self, df: pd.Series) -> pd.Series:
        return (
            df.pipe(self.pipe_drop_duplicates)
            .pipe(self.pipe_location)
            .pipe(self.pipe_vaccine)
            .pipe(self.pipe_select_output_columns)
            .sort_values(by="date")
        )

    def to_csv(self, paths):
        """Generalized."""
        output_file = paths.tmp_vax_out(self.location)
        last_update = pd.read_csv(output_file).date.max()
        df = self.read(last_update)
        if not df.empty and "people_vaccinated" in df.columns:
            df = df.pipe(self.pipeline)
            df = merge_with_current_data(df, output_file)
            df = df.pipe(self.pipe_drop_duplicates)
            df.to_csv(output_file, index=False)


def main(paths):
    Hungary().to_csv(paths)


if __name__ == "__main__":
    main()